# TTS Modal API

This project provides an easy way to launch a minimalistic version of Kokoro and Zonos on Modal. Modal offers a monthly credit of $30 and allows you to rent GPUs, making it a cost-effective solution for running your AI applications.

# WHAT IS INSIDE:
- kokoro_remsky.py : launch https://github.com/remsky/Kokoro-FastAPI in modal
- kokoro_api.py: rebuild of a simple fastapi based on openAI, handle just mp3, a bit faster then remsky
- zonos_og.py: launch https://github.com/Zyphra/Zonos

# Create a Modal Account (needed for all)
- Visit [modal.com](https://modal.com) and sign up for an account.

# For kokoro_remsky and zonos_og:
You just need modal so any python will do as long as you can have a decently recent modal, check on their website for compatibilities
```bash
python3 -m pip install modal
python3 -m modal setup
```

## Kokoro launch:
```bash
modal serve kokoro_remsky.py
```
- you will get a link, click on it and add /docs to see the swagger of fastapi

## Zonos launch:
```bash
modal serve zonos_og.py
```
- you will get an url in the text click on it, it will launch the container
- when the container is launched it will provide a public gradio url, click on it
- the init take a while, once the loading is finished you can use it
- the first launch of a generation takes long as it still need to load some other stuff
- Subsequent generation on a A100 was around 1.42x real time

## Performance
- kokoro_remsky seems to be in the 20-25x real time range  on a T4
- zonos_og seems to be around 1.40x on a A100


# For kokoro_api:
You need to install a bunch of lib so better go with a virtual env
### 2. Set Up Your Virtual Environment
Tested on python3.11 but anything that won't block the startup so mostly same version will work as the code is all executed remotly anyway
```bash
python3 -m venv venv
source venv/bin/activate
```
### 3. Install the Modal Python Package
Open your terminal and run:
```bash
pip install -r requirements.txt
```
There is probably a way to not install anything other then modal localy, when I tried I kept getting multiple reload of some packages so will let like that for now. I dont't really understand modal.
### 4. Link modal
```bash
modal setup
```
or
```bash
python -m modal setup
```
### 5. Launch
```bash
modal serve kokoro_api.py
```
### URL
A URL will be provided in the terminal. Use this URL to link your OpenAI AI instance to this project.
As long as you don't change the name of the project your url will stay the same between restart.
The url will look something like this:
```bash
https://username--project_name-api-dev.modal.run/
```
A lot of project will enable the export of an env key so export this url/v1
```bash
export OPENAI_BASE_URL=https://username--project_name-api-dev.modal.run/v1
```
The swagger of fastapi will be ready at this url/docs
### Performance

Based on our tests:

- Recommended GPU: T40 for cost efficiency
- Speed: Approximately 25–30× real time performance
- First request is slow, taking like 30-60 sec to load it all

Quick numbers:
- 30$ per month of free credits
- 0.6$ the hour of T4
- So around 50h of T4 GPU
- At 20-30x real time that's 1000-1500h of TTS a month for free

### Limitation
- Multi-Voice Support: Currently not available
- Streaming: Streaming functionality is not supported yet
- Only MP3 raw output supported for now

### Eample output KOKORO

```bash
[2025-02-24T15:11:21.313996] 💪 STARTING ASGI 💪
[2025-02-24T15:11:34.932590] 🔥 Initializing pipeline: a...
/usr/local/lib/python3.11/site-packages/torch/nn/modules/rnn.py:123: UserWarning: dropout option adds dropout after all but last recurrent layer, so non-zero dropout expects num_layers greater than 1, but got dropout=0.2 and num_layers=1
  warnings.warn(
/usr/local/lib/python3.11/site-packages/torch/nn/utils/weight_norm.py:143: FutureWarning: `torch.nn.utils.weight_norm` is deprecated in favor of `torch.nn.utils.parametrizations.weight_norm`.
  WeightNorm.apply(module, name, dim)
[2025-02-24T15:12:09.870241]  ✅ Pipeline initialized: a
[2025-02-24T15:12:09.870334] 🎙️ Processing: 
In circuits bright and l ... k you—reach the sky!
    
[2025-02-24T15:12:14.029440] 🎵 AUDIO SEND 🎵 - GPU: T4 | Compute Time: 52.61s | Speed Ratio: 1.39
   POST /v1/audio/speech -> 200 OK  (duration: 65.4 s, execution: 52.7 s)
[2025-02-24T15:12:17.287513] 🎙️ Processing: 
In circuits bright and l ... k you—reach the sky!
    
[2025-02-24T15:12:19.888956] 🎵 AUDIO SEND 🎵 - GPU: T4 | Compute Time: 2.68s | Speed Ratio: 27.37
   POST /v1/audio/speech -> 200 OK  (duration: 2.79 s, execution: 2.72 s)
[2025-02-24T15:12:28.071224] 🎙️ Processing: 
In circuits bright and l ... k you—reach the sky!
    
[2025-02-24T15:12:30.650091] 🎵 AUDIO SEND 🎵 - GPU: T4 | Compute Time: 2.62s | Speed Ratio: 27.93
   POST /v1/audio/speech -> 200 OK  (duration: 2.79 s, execution: 2.66 s)
Disconnecting from Modal - This will terminate your Modal app in a few seconds.
```
