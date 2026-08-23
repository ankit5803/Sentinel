import gradio as gr
from backend.app.main import app as fastapi_app

# The Trojan Horse: A dummy Gradio UI that does nothing but hold our API
demo = gr.Blocks()

with demo:
    gr.Markdown("# 🛡️ Sentinel Core")
    gr.Markdown("The Sentinel Risk Engine API is currently active and processing requests.")
    gr.Markdown("Access the interactive documentation at: **`/docs`**")

# This is the magic line: It mounts your entire FastAPI backend directly into the Gradio web server!
app = gr.mount_gradio_app(fastapi_app, demo, path="/")