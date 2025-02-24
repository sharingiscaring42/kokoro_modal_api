# Minimalistic Kokoro on Modal

This project provides an easy way to launch a minimalistic version of Kokoro on Modal. Modal offers a monthly credit of $30 and allows you to rent GPUs, making it a cost-effective solution for running your AI applications. Our tests have shown that the T40 GPU is the most cost-efficient option, delivering speeds of approximately 25–30× real time.

## Getting Started

### 1. Create a Modal Account
- Visit [modal.com](https://modal.com) and sign up for an account.

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
```bash
python -m modal setup
```
### 5. Launch
```bash
modal serve main.py
```
### URL
A URL will be provided in the terminal. Use this URL to link your OpenAI AI instance to this project.
As long as you don't change the name of the project your url will stay the same between restart.
The url will look something like this:
```bash
https://username--project_name-api-dev.modal.run/
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


### Eample output

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