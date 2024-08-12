# WaifuAssistant

The Unified assistatnt for waifu lovers.

The goal of this project is that the girl recognize user's personality, emotion and voice. So that, in given context, the girl should response correct voice, text and face.

# Demo

[![IMAGE ALT TEXT HERE](https://github.com/user-attachments/assets/91f2d62b-11d2-4d32-aa8f-03ef8dfdae7a)
](https://www.youtube.com/watch?v=_Jzv1-Y8-HM)

## feature

- [Chatbot](https://huggingface.co/spow12/ChatWaifu_v1.2.1)
- [TTS](https://huggingface.co/spow12/visual_novel_tts)
- [ASR](https://huggingface.co/spow12/Visual-novel-transcriptor)
- [VtubeStudio](https://denchisoft.com/)

## WIP feature

- Response with emotion
- Recongnize user's emotion
- Recongnize User's screen 

# How to run

Clone server-side repository(this repository)

```bash
git clone https://github.com/yw0nam/WaifuAssistant
cd WaifuAssistant
```

You should adjust port, huggingface cache path, db path.. etc in docker-compose.yaml

After that,

```bash
docker-compose build
```

```bash
docker-compose up
```

After running server side,

Clone local-side [repository](https://github.com/yw0nam/WaifuAssistant_local)

```bash
git clone https://github.com/yw0nam/WaifuAssistant_local
cd WaifuAssistant_local
```

```bash
conda create -n WaifuAssistant_local python=3.10
conda activate WaifuAssistant_local
pip install -r requirements.txt
```
- Install [VTS desktop audio plugin](https://www.youtube.com/watch?v=IiZ0JrGd6BQ&t=11s) by [Lua Lucky](https://www.youtube.com/watch?v=IiZ0JrGd6BQ&t=11s)
- open it and connect to Vtube Studio

After that, you can run the code,
```python
python main.py
```
