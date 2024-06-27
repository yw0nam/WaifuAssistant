from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from WaifuChat.Chat import ChatWaifu
from omegaconf import OmegaConf
from WaifuChat.utils import (
    InitPromptRequest,
    CompletionRequest,
    CompletionResponse,
    load_chara_background_dict,
)

configs = OmegaConf.load('./WaifuChat/config.yaml')

chara_background = load_chara_background_dict()
app = FastAPI(
    title="Inference API",
    description="API for speech inference using binary WAV data",
    version="1.0",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
waifuchat = ChatWaifu(configs=configs, chara_background=chara_background)

# To do:
# Move dictionary to db
chat_dicts = {}
# Endpoint for init_prompt_and_comp
@app.post("/init_prompt_and_comp", response_model=CompletionResponse)
def init_prompt_and_completion(request: InitPromptRequest):
    try:
        message = waifuchat.init_prompt(
            chara=request.chara, 
            query=request.query, 
            situation=request.situation
        )            
        message, chat_id = waifuchat.request_completion(
                message,
                request.generation_config
            )
        chat_dicts[chat_id] = message
        chara_response = message[-1]['content']
        return CompletionResponse(chara_response=chara_response, chat_id=chat_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint for request_completion
@app.post("/request_completion", response_model=CompletionResponse)
def request_completion(request: CompletionRequest):
    try:
        if request.chat_id == "":
            raise HTTPException(status_code=500, detail="You shoud initilize a chat first")
        if request.user_query != "":
            message, chat_id = waifuchat.request_completion_with_user_message(
                request.user_query,
                chat_dicts[request.chat_id],
                request.generation_config
            )
        else:
            message = waifuchat.request_completion(
                chat_dicts[request.chat_id],
                request.generation_config
            )   
        chat_dicts[request.chat_id] = message
        chara_response = message[-1]['content']
        return CompletionResponse(chara_response=chara_response, chat_id=chat_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))