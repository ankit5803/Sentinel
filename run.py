import sys
import os

# 1. Force Python to look inside the 'backend' folder
sys.path.insert(0, os.path.abspath("backend"))

import gradio as gr
from app.main import app as fastapi_app
import uvicorn

# 2. Dummy Gradio UI wrapper
demo = gr.Blocks()
with demo:
    gr.Markdown("# 🛡️ Sentinel Core API")
    gr.Markdown("The Sentinel Risk Engine is currently active.")
    gr.Markdown("Access the interactive documentation at: **`/docs`**")

# 3. Mount the API
app = gr.mount_gradio_app(fastapi_app, demo, path="/")

# 4. THIS IS THE MISSING PIECE: Keep the server awake and listening!
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)