from pydantic import BaseModel, Field, ValidationError

class AnalyzeRequest(BaseModel):
    """
    Incoming request schema. Ensures FastAPI automatically rejects 
    malformed payloads before they ever reach the Risk Engine.
    """
    text: str = Field(
        ..., 
        min_length=1, 
        max_length=2000, 
        description="The raw text to analyze for violent threat risk."
    )

class RiskDecision(BaseModel):
    """
    Outgoing response schema mapping strictly to the Sentinel Architecture rules.
    This is what the frontend or external clients will receive.
    """
    threat_probability: float = Field(..., ge=0.0, le=1.0)
    risk_level: str = Field(..., description="Calculated risk bucket: SAFE, REVIEW, or HIGH RISK")
    immediacy: str = Field(..., description="Estimated timeline: LOW, MEDIUM, or HIGH")
    target_identified: bool = Field(..., description="True if specific entities/people are targeted")
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: str = Field(..., description="Explainable string detailing why this score was generated")

# --- Quick Test ---
if __name__ == "__main__":
    print("Testing AnalyzeRequest Schema...")
    
    # 1. Valid Data Test
    valid_data = {"text": "This is a normal sentence."}
    parsed = AnalyzeRequest(**valid_data)
    print(f"✅ Valid request parsed: {parsed.model_dump()}")

    # 2. Invalid Data Test (Empty string violates min_length=1)
    print("\nTesting Invalid Data (empty string)...")
    try:
        invalid_data = {"text": ""}
        AnalyzeRequest(**invalid_data)
    except ValidationError as e:
        print("✅ Caught invalid request successfully! Here is the error Pydantic generated:")
        print(e)