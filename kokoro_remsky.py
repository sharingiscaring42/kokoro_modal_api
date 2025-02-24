import modal
import os
import sys
import subprocess

gpu_config = "T4"
image = (
    modal.Image.from_registry("pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel")
    .apt_install("git", "sed", "espeak-ng","ffmpeg", gpu=gpu_config)
    .run_commands(
        "git clone https://github.com/remsky/Kokoro-FastAPI.git && "
        "cd Kokoro-FastAPI && "
        "pip install -e .[gpu] && "
        # "pip install -e .",
        "python3 docker/scripts/download_model.py --output api/src/models/v1_0",
        gpu=gpu_config
    )
    .pip_install()
)
app = modal.App(name="Kokoro-FastAPI")

@app.function(image=image,gpu=gpu_config,timeout=86400,concurrency_limit=1)
@modal.asgi_app()
def fastapi():
    folder_dir = "/Kokoro-FastAPI"
    # Ensure the repository directory the working folder.
    os.chdir(folder_dir)
    # Ensure the repository directory is in sys.path.
    if folder_dir not in sys.path:
        sys.path.insert(0, folder_dir)

    # Set environment variables
    os.environ["USE_GPU"] = "true"
    os.environ["USE_ONNX"] = "false"
    os.environ["MODEL_DIR"] = "src/models"
    os.environ["VOICES_DIR"] = "src/voices/v1_0"
    os.environ["WEB_PLAYER_PATH"] = "/app/web"
    os.environ["PYTHONPATH"] = "/app:/app/api"
    os.environ["DOWNLOAD_MODEL"] = "true"


    from api.src.main import app as kokoro_app  # Direct import
   
    # Build and launch directly
    
    return kokoro_app