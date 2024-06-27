import json
from huggingface_hub import hf_hub_download
from pydantic import BaseModel
from typing import Optional

def load_chara_background_dict(repo_id='spow12/ChatWaifu', filename='system_dict.json', local_dir='./'):
    try:
        with open('./system_dict.json', 'r') as f:
            chara_background_dict = json.load(f)
    except:
        hf_hub_download(repo_id=repo_id, filename=filename, local_dir=local_dir)
        with open('./system_dict.json', 'r') as f:
            chara_background_dict = json.load(f)
    return chara_background_dict

class InitPromptRequest(BaseModel):
    chara: str
    query: str
    situation: Optional[str] = ""
    generation_config: Optional[dict] = {'top_p': 0.5, 'temperature': 0.9}
    
class CompletionRequest(BaseModel):
    chat_id: str = ""
    user_query: Optional[str] = ""
    generation_config: Optional[dict] = {'top_p': 0.5, 'temperature': 0.9}

class CompletionResponse(BaseModel):
    chara_response: str
    chat_id: str
    
    
