import sys
import os

# 1. Force Python to look inside the 'backend' folder for all imports
sys.path.insert(0, os.path.abspath("backend"))

# 2. NOW we can safely import Gradio and FastAPI
import gradio as gr
from app.main import app as fastapi_app

# 3. Mount the API to Hugging Face's Gradio interface
demo = gr.Blocks()
with demo:
    gr.Markdown("# 🛡️ Sentinel Core API")
    gr.Markdown("The Sentinel Risk Engine is currently active.")
    gr.Markdown("Access the interactive documentation at: **`/docs`**")

app = gr.mount_gradio_app(fastapi_app, demo, path="/")