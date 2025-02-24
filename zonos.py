import modal
import os
import sys
import subprocess

gpu_config = "A100"
image_zonos = (
    modal.Image.from_registry("pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel")
    .apt_install("git", "sed", "espeak-ng", gpu=gpu_config)
    .run_commands(
        "git clone https://github.com/Zyphra/Zonos.git && "
        "cd Zonos && "
        "pip install -e .",
        gpu=gpu_config
    )
)
app = modal.App(name="Zonos_default")

@app.function(image=image_zonos,gpu=gpu_config,timeout=86400,)
@modal.web_server(port=7860, startup_timeout=99999999999)
def gradio_interface():
    zonos_dir = "/Zonos"
    # Ensure the repository directory the working folder.
    os.chdir(zonos_dir)
    # Ensure the repository directory is in sys.path.
    if zonos_dir not in sys.path:
        sys.path.insert(0, zonos_dir)
    from gradio_interface import build_interface  # Direct import
   
    # Build and launch directly
    demo = build_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,  # Enable gradio sharing
        prevent_thread_lock=False,  # Required for Modal
        debug=False,
    )