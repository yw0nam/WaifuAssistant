from fastapi import FastAPI, HTTPException
from fastapi.responses import Response, JSONResponse
from scipy.io import wavfile
from io import BytesIO
from WaifuChat.Chat import ChatWaifu
from omegaconf import OmegaConf
from WaifuChat.utils import (
    InitPromptRequest,
    CompletionRequest,
    CompletionResponse,
    AudioRequest,
    AudioResponse,
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
@app.post("/init_prompt_and_comp")
def init_prompt_and_completion(request: InitPromptRequest):
    try:
        message = waifuchat.init_prompt(
            chara=request.chara, 
            query=request.query,
            history=request.history,
            situation=request.situation
        )            
        message, chat_id = waifuchat.request_completion(
                message,
                request.generation_config
            )
        chat_dicts[chat_id] = message
        return JSONResponse(message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint for request_completion
@app.post("/request_completion", response_model=CompletionResponse)
def request_completion(request: CompletionRequest):
    try:
        if request.chat_id == "":
            raise HTTPException(status_code=500, detail="You shoud initilize a chat first")
        if request.query != "":
            message, chat_id = waifuchat.request_completion_with_user_message(
                request.query,
                chat_dicts[request.chat_id],
                request.generation_config
            )
        else:
            message = waifuchat.request_completion(
                chat_dicts[request.chat_id],
                request.generation_config
            )   
        chat_dicts[request.chat_id] = message
        return JSONResponse(message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/request_tts", response_class=AudioResponse)
def request_completion(request: AudioRequest):
    try:
        wav = waifuchat.request_tts(request.chara, request.chara_response)
        with BytesIO() as wavContent:
            wavfile.write(wavContent, configs.tts_configs.sr, wav)
            return Response(content=wavContent.getvalue(), media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    