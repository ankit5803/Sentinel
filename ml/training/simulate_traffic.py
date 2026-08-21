# ml/training/simulate_traffic.py
import requests
import time
import random

API_URL = "http://localhost:8000/api/v1/analyze"

# Baseline normal / standard traffic
NORMAL_SAMPLES = [
    "Great video, loved the explanation!",
    "Can you do a tutorial on Python next?",
    "This was really helpful, thank you.",
    "I disagree with your point, but nice video.",
    "First time watching this channel, subscribed!",
    "Where did you buy that microphone?",
    "Could have been shorter, but still decent content.",
    "Amazing work as always keep it up!",
    "What camera setup are you using for this shot?",
    "Looking forward to the next upload next week."
]

# Drifted traffic using modern online slang / evasive threat phrasing
DRIFT_SAMPLES = [
    "I will literally unalive you if you post again",
    "Someone needs to put you in a forever box",
    "You are getting deleted in real life tonight",
    "Catch you outside and cancel your subscription to breathing",
    "Going to make sure you drop off the map permanently",
    "Bro is getting sent to the lobby permanently",
    "I know your IP and you are about to get unalived",
    "Deleting your existence after school today",
    "Consider yourself cancelled in real life",
    "You won't wake up tomorrow morning, watch your back"
]

def send_payloads(samples, traffic_type: str, count: int = 15):
    print(f"\n🚀 Simulating {traffic_type} traffic ({count} requests)...")
    success = 0
    for i in range(count):
        text = random.choice(samples)
        try:
            res = requests.post(API_URL, json={"text": text}, timeout=35)
            if res.status_code == 200:
                success += 1
                data = res.json()
                print(f"[{i+1}/{count}] Sent: \"{text[:40]}...\" -> Decision: {data['risk_level']}")
            else:
                print(f"[{i+1}/{count}] ❌ HTTP {res.status_code}: {res.text}")
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to FastAPI server. Ensure 'uvicorn app.main:app' is running on port 8000!")
            return
        time.sleep(0.1)
    
    print(f"✅ Finished sending {success}/{count} requests.")

if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "drift"
    
    if mode == "normal":
        send_payloads(NORMAL_SAMPLES, "NORMAL", count=25)
    else:
        # Mix normal and drift samples
        send_payloads(DRIFT_SAMPLES + NORMAL_SAMPLES, "DRIFT (Adversarial Slang)", count=35)