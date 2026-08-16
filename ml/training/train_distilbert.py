"""
Fine-tune DistilBERT for threat classification. Run once per language:
    python train_distilbert.py english
    python train_distilbert.py hinglish

Model choice:
    english  -> distilbert-base-uncased
    hinglish -> distilbert-base-multilingual-cased (handles code-mixed/Romanized
                text better than the English-only model)

Handles class imbalance with a WEIGHTED loss (inverse class frequency), same
principle as class_weight='balanced' in the baseline — without this the model
would just learn to always predict SAFE given how skewed the data is.

Tuned for a 4GB VRAM GPU (e.g. RTX 3050 laptop):
    - small per-device batch size (8) + gradient accumulation (2) to
      simulate an effective batch size of 16 without running out of memory
    - fp16 mixed precision training (roughly halves memory use)
    - max_length=128 tokens (these are short social-media sentences, not
      long documents, so this is plenty and keeps memory down)

Output: ml/training/artifacts/{language}_distilbert/
    Contains the fine-tuned model, tokenizer, and label2id/id2label mapping.
"""

import sys
import csv
import json
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.utils.class_weight import compute_class_weight
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
)

DATA_DIR = Path(__file__).parent.parent / "data" / "processed"
ARTIFACTS_DIR = Path(__file__).parent / "artifacts"

MODEL_NAME_BY_LANGUAGE = {
    "english": "distilbert-base-uncased",
    "hinglish": "distilbert-base-multilingual-cased",
}

MAX_LENGTH = 128
BATCH_SIZE = 8
GRAD_ACCUM_STEPS = 2  # effective batch size = BATCH_SIZE * GRAD_ACCUM_STEPS = 16
NUM_EPOCHS = 3
LEARNING_RATE = 2e-5


def load_split(language: str, split: str) -> tuple[list[str], list[str]]:
    path = DATA_DIR / f"{language}_{split}.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path} not found — run build_training_set.py first")

    sentences, labels = [], []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            sentences.append(row["sentence"])
            labels.append(row["label"])
    return sentences, labels


class ThreatDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {k: v[idx] for k, v in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item


class WeightedLossTrainer(Trainer):
    """Trainer subclass that applies class weights to the loss, so the model
    doesn't just learn to always predict the majority class (SAFE)."""

    def __init__(self, class_weights: torch.Tensor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        loss_fct = torch.nn.CrossEntropyLoss(weight=self.class_weights.to(logits.device))
        loss = loss_fct(logits, labels)
        return (loss, outputs) if return_outputs else loss


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    macro_f1 = f1_score(labels, preds, average="macro", zero_division=0)
    return {"macro_f1": macro_f1}


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("english", "hinglish"):
        print("Usage: python train_distilbert.py <english|hinglish>")
        sys.exit(1)

    language = sys.argv[1]
    model_name = MODEL_NAME_BY_LANGUAGE[language]
    print(f"=== Fine-tuning DistilBERT for: {language} ({model_name}) ===\n")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    if device == "cpu":
        print("[WARN] CUDA not available — this will be very slow on CPU for a transformer.")

    X_train, y_train_str = load_split(language, "train")
    X_val, y_val_str = load_split(language, "val")

    # Build label mapping from whatever classes actually appear in training data
    # (English is effectively binary, Hinglish has 3 classes present — see
    # PROJECT_CONTEXT.md for why POTENTIAL_THREAT/VIOLENT_THREAT are sparse/absent).
    labels_sorted = sorted(set(y_train_str))
    label2id = {label: i for i, label in enumerate(labels_sorted)}
    id2label = {i: label for label, i in label2id.items()}
    print(f"Classes: {labels_sorted}\n")

    y_train = [label2id[l] for l in y_train_str]
    y_val = [label2id[l] for l in y_val_str]

    print("Loading tokenizer + model...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=len(labels_sorted),
        id2label=id2label,
        label2id=label2id,
    )
    model.to(device)

    print("Tokenizing...")
    train_encodings = tokenizer(
        X_train, truncation=True, padding=True, max_length=MAX_LENGTH, return_tensors="pt"
    )
    val_encodings = tokenizer(
        X_val, truncation=True, padding=True, max_length=MAX_LENGTH, return_tensors="pt"
    )

    train_dataset = ThreatDataset(train_encodings, y_train)
    val_dataset = ThreatDataset(val_encodings, y_val)

    # Inverse-frequency class weights — same imbalance-handling principle as
    # class_weight='balanced' in the sklearn baseline.
    class_weights = compute_class_weight(
        class_weight="balanced",
        classes=np.array(sorted(label2id.values())),
        y=np.array(y_train),
    )
    class_weights_tensor = torch.tensor(class_weights, dtype=torch.float32)
    print(f"Class weights: {dict(zip(labels_sorted, class_weights.round(2)))}\n")

    output_dir = ARTIFACTS_DIR / f"{language}_distilbert"

    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM_STEPS,
        learning_rate=LEARNING_RATE,
        fp16=(device == "cuda"),  # mixed precision only makes sense on GPU
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="macro_f1",
        greater_is_better=True,
        logging_steps=50,
        report_to="none",  # don't try to log to wandb/etc by default
    )

    trainer = WeightedLossTrainer(
        class_weights=class_weights_tensor,
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
    )

    print("Starting training...\n")
    trainer.train()

    print("\n=== Final evaluation on validation set ===")
    predictions = trainer.predict(val_dataset)
    preds = np.argmax(predictions.predictions, axis=-1)
    pred_labels = [id2label[p] for p in preds]
    true_labels = [id2label[l] for l in y_val]

    print(classification_report(true_labels, pred_labels, zero_division=0))
    print("Confusion matrix:")
    labels_order = sorted(set(true_labels) | set(pred_labels))
    print(f"Labels order: {labels_order}")
    cm = confusion_matrix(true_labels, pred_labels, labels=labels_order)
    for row in cm:
        print(row)

    # Save final model, tokenizer, and label mapping
    output_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    with open(output_dir / "label_mapping.json", "w") as f:
        json.dump({"label2id": label2id, "id2label": id2label}, f, indent=2)

    print(f"\nSaved model, tokenizer, and label mapping to: {output_dir}")


if __name__ == "__main__":
    main()