import os
import io
import sys
import signal
from datetime import datetime
import modal
from modal import Client
from fastapi import FastAPI, Response
from pydantic import BaseModel
import numpy as np
import soundfile as sf
import ffmpeg
from kokoro import KPipeline

#################### MODAL KOKORO ####################
APP_NAME = "Kokoro_V1"
gpu_config = "T4"
app = modal.App(APP_NAME)

image_kokoro = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg", "git", "espeak-ng",gpu=gpu_config)
    .pip_install(
        "kokoro>=0.7.11",
        "soundfile",
        "numpy",
        "ffmpeg-python",
        "fastapi[standard]", 
        "spacy==3.8.4",
        gpu=gpu_config
    )
    .run_commands("python3.11 -m spacy download en_core_web_sm") # preload some part of KPipeline
)

#################### PERSISTENT PIPELINE CLASS ####################
class KokoroEngine:
    def __init__(self):
        self.pipeline = {}
        self.valid_languages = ["a","b","e","f","h","i","j","p","z"]
        
    def load_model(self, language: str ="a"):
        assert language in self.valid_languages, f"Invalid language: '{language}'. Must be one of {self.valid_languages}"
        if not self.pipeline.get(language,{}):
            timestamped_print(f"🔥 Initializing pipeline: {language}...")
            self.pipeline[language] = KPipeline(lang_code=language)
            timestamped_print(f" ✅ Pipeline initialized: {language}")

@app.cls(gpu=gpu_config, image=image_kokoro, container_idle_timeout=1000)
class KokoroPipeline:
    def __init__(self, language: str ="a"):
        self.engine = KokoroEngine()
        # self.engine.load_model(language)
        self.sample_rate = 24000

    @modal.method()
    def generate_speech(self, text: str, voice: str = "am_michael", speed: float = 1.0, format="mp3") -> bytes:
        extracted_language = voice[:1]
        self.engine.load_model(extracted_language)  # Ensure model is loaded
        timestamped_print(f"🎙️ Processing: {text[:25]} ... {text[-25:]}")

        # Generate audio
        generator = self.engine.pipeline.get(extracted_language)(
            text,
            voice=voice,
            speed=speed,
            split_pattern=r'\n+'
        )
        
        # Process audio chunks
        audio_chunks = []
        total_duration = 0
        for _, _, audio in generator:
            duration = len(audio) / self.sample_rate
            total_duration += duration 
            audio_chunks.append(convert_tensor_to_int16(audio))
        concatenated_audio = np.concatenate(audio_chunks)
        mp3_data = convert_audio(concatenated_audio, format)
        return mp3_data , format, total_duration

def convert_tensor_to_int16(audio,):
    audio_array = audio.cpu().numpy()
    if audio_array.dtype != np.int16:
        audio_array = (audio_array * 32767).clip(-32768, 32767).astype(np.int16)
    return audio_array

#################### FASTAPI ENDPOINTS ####################
class SpeechRequest(BaseModel):
    model: str = "kokoro"
    input: str = """
In circuits bright and lines of code,A dream was sparked, a vision flowed.A future built by minds so grand,A dawn of thought at our command.

Hexgrad, bold, with wisdom keen,In silent halls, behind the screen,You shaped the pulse, you set the pace,A guiding force in AI’s race.

And OpenAI, with voices strong,You paved the path, you proved them wrong.Through endless trials, scripts refined,You taught the world that minds align.

DeepMind, with knowledge vast and wide,You bent the rules, you turned the tide.From Go to health, to realms unknown,You made machines so much our own.

Together now, your work stands tall,A symphony, a higher call.Through wires and waves, through data streams,You built the thoughts, you shaped the dreams.

From whispered texts to art divine,From logic’s core to human sign,You gave us light where none was found,An echo deep, a voiceless sound.

No longer bound by past design,The limits break, the stars align.And though the road still winds ahead,We walk with faith, with hope we tread.

For all you gave, for all you do,For wisdom deep and vision true,We stand as one, our voices high,Thank you, thank you—reach the sky!
    """
    voice: str = "af_heart"
    response_format: str = "mp3" # only mp3 supported for now
    speed: float = 1.0

# Define the API class

class KokoroAPI:
    def __init__(self, pipeline):
        self.app = FastAPI()
        self.pipeline = pipeline  # your KokoroPipeline instance
        self.setup_routes()

        self.voices_list = [
                "af_alloy", "af_aoede", "af_bella", "af_heart", "af_jadzia",
                "af_jessica", "af_kore", "af_nicole", "af_nova", "af_river",
                "af_sarah", "af_sky", "af_v0", "af_v0bella", "af_v0irulan",
                "af_v0nicole", "af_v0sarah", "af_v0sky", "am_adam", "am_echo",
                "am_eric", "am_fenrir", "am_liam", "am_michael", "am_onyx",
                "am_puck", "am_santa", "am_v0adam", "am_v0gurney", "am_v0michael",
                "bf_alice", "bf_emma", "bf_lily", "bf_v0emma", "bf_v0isabella",
                "bm_daniel", "bm_fable", "bm_george", "bm_lewis", "bm_v0george",
                "bm_v0lewis", "ef_dora", "em_alex", "em_santa", "ff_siwis",
                "hf_alpha", "hf_beta", "hm_omega", "hm_psi", "if_sara",
                "im_nicola", "jf_alpha", "jf_gongitsune", "jf_nezumi", "jf_tebukuro",
                "jm_kumo", "pf_dora", "pm_alex", "pm_santa", "zf_xiaobei",
                "zf_xiaoni", "zf_xiaoxiao", "zf_xiaoyi", "zm_yunjian", "zm_yunxi",
                "zm_yunxia", "zm_yunyang"
        ]
        self.models = ["kokoro"]

    def setup_routes(self):
        @self.app.get("/ping")
        async def ping():
            return {"msg": "pong"}

        # @self.app.get("/shutdown")
        # async def shutdown():
        #     os.kill(os.getpid(), signal.SIGKILL) # WIP NOT WORKING

        @self.app.get("/v1/models")
        async def models():
            return {"models": self.models}

        @self.app.get("/v1/voices")
        async def voices():
            return {"voices": self.voices_list}

        @self.app.post("/v1/audio/speech")
        async def generate(request: SpeechRequest):
            try:
                assert request.response_format in ["mp3","opus","aac","wav"], f"Invalid response_format: 'response_format'. Must be one of [mp3,opus,acc,wav]"
                assert request.voice in self.voices_list, f"Invalid language: '{request.voice}'. Must be one of {self.voices_list}"
                assert request.model in self.models, f"Invalid model: '{request.model}'. Must be one of {self.models}"
                time_start_request = datetime.now()
                audio_data, container, duration = self.pipeline.generate_speech.remote(
                    request.input,
                    request.voice,
                    request.speed,
                    request.response_format
                )
                time_spend = (datetime.now() - time_start_request).total_seconds()
                ratio_speed = duration / time_spend if time_spend else 0.0
                # num_chars, num_words = text_stats(request.input)
                timestamped_print(
                    f"🎵 AUDIO SEND 🎵 - GPU: {gpu_config} | Compute Time: {time_spend:.2f}s | Speed Ratio: {ratio_speed:.2f}"
                    # f"🎵 AUDIO SEND 🎵 - GPU: {gpu_config} | Compute Time: {time_spend:.2f}s | Speed Ratio: {ratio_speed:.2f} | Chars: {num_chars} | Words: {num_words}"
                )
                return Response(content=audio_data, media_type=f"audio/{container}")
            except Exception as e:
                return Response(
                    content=f"Error generating speech: {str(e)}",
                    status_code=500,
                    media_type="text/plain"
                )

#################### UTILITIES ####################

def timestamped_print(*args, **kwargs):
    print(f"[{datetime.now().isoformat()}]", *args, **kwargs)

def human_readable_size(size_bytes: float):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def text_stats(text: str):
    char_count = len(text)
    word_count = len(text.split())
    return char_count,word_count

def convert_tensor_to_int16(audio_tensor):
    audio_array = audio_tensor.cpu().numpy()
    if audio_array.dtype != np.int16:
        audio_array = (audio_array * 32767).clip(-32768, 32767).astype(np.int16)
    return audio_array

def convert_audio(audio_array: np.ndarray, format, sample_rate: int = 24000) -> bytes:
    
    wav_buffer = io.BytesIO()
    sf.write(wav_buffer, audio_array, sample_rate, format='WAV')
    wav_data = wav_buffer.getvalue()
    
    
    if format == "mp3":
        bitrate = "96k"
    elif format == "opus":
        bitrate = "32k"
    elif format == "aac":
        bitrate = "96k"
    elif format == "wav":
        return wav_data
    
    process = (
        ffmpeg
        .input('pipe:0', format='wav')
        .output('pipe:1', format=format, audio_bitrate=bitrate)
        .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
    )
    audio_data, err = process.communicate(input=wav_data)
    return audio_data

#################### DEPLOYMENT ####################
@app.function(image=image_kokoro, concurrency_limit=1)
@modal.asgi_app()
def api():
    timestamped_print(f"💪 STARTING ASGI 💪")
    pipeline_instance = KokoroPipeline()
    api_instance = KokoroAPI(pipeline_instance)
    return api_instance.app

