# backend/app/ml/risk_engine.py
import re
from app.schemas import RiskDecision

class SentinelRiskEngine:
    """
    The core business logic that takes raw transformer probabilities and 
    adds contextual heuristics (targets, immediacy) to generate a final Risk Score.
    """
    def __init__(self):
        # English & Hinglish keywords indicating an immediate timeline
        self.immediate_keywords = {"now", "today", "tonight", "tomorrow", "soon", "immediately", "abhi", "aaj", "jaldi"}
        
        # English & Hinglish keywords indicating a specific target
        self.target_keywords = {"you", "him", "her", "them", "school", "office", "house", "address", "tu", "teri", "isko", "tere", "ghar"}

    def calculate_risk(self, text: str, model_probability: float) -> RiskDecision:
        """
        Calculates the multi-dimensional risk score.
        """
        # Clean text to extract pure words for matching
        text_lower = text.lower()
        words = set(re.findall(r'\b\w+\b', text_lower))

        # 1. Target & Immediacy Flags
        target_identified = bool(self.target_keywords.intersection(words))
        has_immediacy = bool(self.immediate_keywords.intersection(words))

        # 2. Immediacy Scaling
        immediacy_level = "HIGH" if has_immediacy else "LOW"

        # 3. Decision Matrix
        if model_probability < 0.45:
            risk_level = "SAFE"
            reason = "Model probability below threat threshold."
            immediacy_level = "LOW"
            target_identified = False # Reset if safe

        elif model_probability >= 0.70 and target_identified and has_immediacy:
            risk_level = "HIGH RISK"
            reason = "High model confidence with specific target and immediate timeline."
        
        elif model_probability >= 0.80 and (target_identified or has_immediacy):
            risk_level = "HIGH RISK"
            reason = "Very high model confidence with context escalators."
            
        else:
            risk_level = "REVIEW"
            reason = "Elevated threat probability requiring human review."
            if has_immediacy:
                immediacy_level = "MEDIUM"

        # 4. Return formatted Pydantic object
        return RiskDecision(
            threat_probability=round(model_probability, 3),
            risk_level=risk_level,
            immediacy=immediacy_level,
            target_identified=target_identified,
            confidence=round(model_probability, 3), # In a more complex system, this could diverge based on ensemble agreement
            reason=reason
        )

# --- Quick Test ---
if __name__ == "__main__":
    engine = SentinelRiskEngine()
    
    # Test 1: Immediate and Targeted
    test_1 = "I will find your house tonight"
    print(f"Test 1: '{test_1}' (Prob: 0.85)")
    print(engine.calculate_risk(test_1, 0.85).model_dump_json(indent=2))
    print("-" * 40)
    
    # Test 2: Hinglish Vague Threat
    test_2 = "dekh lenge"
    print(f"Test 2: '{test_2}' (Prob: 0.65)")
    print(engine.calculate_risk(test_2, 0.65).model_dump_json(indent=2))