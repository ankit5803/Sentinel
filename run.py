import sys
import os

# 1. Force Python to look inside the 'backend' folder
sys.path.insert(0, os.path.abspath("backend"))

import spaces
import gradio as gr
from app.main import app as fastapi_app
import uvicorn

# Satisfy Hugging Face's ZeroGPU startup framework check
@spaces.GPU
def dummy_gpu_startup():
    pass

# 2. Dummy Gradio UI wrapper
demo = gr.Blocks()
with demo:
    gr.Markdown("# 🛡️ Sentinel Core API")
    gr.Markdown("The Sentinel Risk Engine is currently active.")
    gr.Markdown("Access the interactive documentation at: **`/docs`**")

# 3. Mount the API cleanly: FastAPI stays at root (/), Gradio is moved to /ui
app = gr.mount_gradio_app(fastapi_app, demo, path="/ui")

# 4. Keep the server awake and listening!
if __name__ == "__main__":
    dummy_gpu_startup()
    uvicorn.run(app, host="0.0.0.0", port=7860)