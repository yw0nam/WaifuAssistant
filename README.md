# WaifuAssistant

The Unified assistatnt for waifu lovers.

The goal of this project is that the girl recognize user's personality, emotion and voice. So that, in given context, the girl should response correct voice, text and face.

# Feature

Here is project [collection](https://huggingface.co/collections/spow12/visual-novel-66416e5e0e40c1344698d675)

## Basic feature

- Chatbot (Done)
- TTS (Done)
- ASR (Done)
- Recognize User's emotion(in progress)
- Generate Girl's Image or model for each response.

## Advance feature

- Response with emotion
- Response about user's emotion

# Dataset

## Data sample
Here is the Dataset samples

Name | dialog_type | text |scene_name | voice_file_name | text_idx  | game_name |
--- | --- | --- | --- | --- |  --- |  --- | 
芦花	| conversation |	人違いならごめんなさい。もしかして、まー坊？	| chapter　1-1-02	| rok001_003 |	49	| SenrenBanka |
芦花	| conversation | やーやー、随分とお久しぶりだね	| chapter　1-1-02 |rok001_005 |	52	| SenrenBanka	| 

## Current dataset

Currently the dataset contains below games

- Senren＊Banka
- Café Stella and the Reaper's Butterflies
- Riddle Joker

Here is feature implement table for each character.

character | visual_novel | TTS | Chatbot |
--- | --- | --- | --- | 
ムラサメ | Senren＊Banka | Done | Done | 
茉子  | Senren＊Banka | Done | Done | 
芳乃  |  Senren＊Banka | Done | Done | 
レナ  | Senren＊Banka | Done | Done | 
千咲  | Senren＊Banka | Done | Done | 
芦花  | Senren＊Banka | Done | Done | 
愛衣  | Café Stella and the Reaper's Butterflies | Done | Done | 
栞那  | Café Stella and the Reaper's Butterflies | Done | Done | 
ナツメ | Café Stella and the Reaper's Butterflies | Done | Done | 
希    | Café Stella and the Reaper's Butterflies | Done | Done | 
涼音  | Café Stella and the Reaper's Butterflies | Done | Done | 
あやせ    | Riddle Joker | Done | Done | 
七海     | Riddle Joker | Done | Done | 
羽月     | Riddle Joker | Done | Done | 
茉優     | Riddle Joker | Done | Done | 
小春     | Riddle Joker | Done | Done | 

I will add more data from Sabbat of the Witch, tenshi☆souzou re-boot! etc...
