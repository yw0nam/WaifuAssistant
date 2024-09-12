from fastapi import FastAPI, HTTPException
from fastapi.responses import Response, JSONResponse
from scipy.io import wavfile
from io import BytesIO
from WaifuChat.Chat import ChatWaifu
from pymongo import MongoClient
from omegaconf import OmegaConf
from WaifuChat.utils import (
    InitPromptRequest,
    CompletionRequest,
    CompletionResponse,
    TTSRequest,
    TTSResponse,
    DBStoreRequest,
    load_chara_background_dict,
    load_sample_chat_dict
)

configs = OmegaConf.load('./WaifuChat/config.yaml')

chara_background = load_chara_background_dict()
sample_chat = load_sample_chat_dict()
app = FastAPI(
    title="Inference API",
    description="API for speech inference using binary WAV data",
    version="1.0",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
waifuchat = ChatWaifu(configs=configs, chara_background=chara_background, sample_chat=sample_chat)
client = MongoClient("mongodb://root:1234@mongodb:27017")
db = client.visual_novel_db  # Replace 'mydatabase' with your actual database name
collection = db.waifuchat_collection  # Replace 'mycollection' with your actual collection name


# To do:
# Move dictionary to db
# Endpoint for init_prompt_and_comp
@app.post("/init_prompt_and_comp")
def init_prompt_and_completion(request: InitPromptRequest):
    try:
        message = waifuchat.init_prompt(
            chara=request.chara, 
            query=request.query,
            situation=request.situation,
            system=request.system
        )
        message = waifuchat.request_completion(
                message,
                request.generation_config
            )
        return JSONResponse(message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint for request_completion
@app.post("/request_completion", response_model=CompletionResponse)
def request_completion(request: CompletionRequest):
    try:
        if request.query != "":
            message = waifuchat.request_completion_with_user_message(
                request.query,
                request.history,
                request.generation_config,
            )
        else:
            message = waifuchat.request_completion(
                message,
                request.generation_config
            )
        return JSONResponse(message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/request_tts", response_class=TTSResponse)
def request_tts(request: TTSRequest):
    try:
        wav = waifuchat.request_tts(request.chara, request.chara_response)
        with BytesIO() as wavContent:
            wavfile.write(wavContent, configs.tts_configs.sr, wav)
            return Response(content=wavContent.getvalue(), media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/request_multi_line_tts", response_class=TTSResponse)
def request_multi_line_tts(request: TTSRequest):
    try:
        wav = waifuchat.request_multi_line_tts(request.chara, request.chara_response)
        with BytesIO() as wavContent:
            wavfile.write(wavContent, configs.tts_configs.sr, wav)
            return Response(content=wavContent.getvalue(), media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/request_store_to_db", response_class=Response)
def request_store_to_db(request: DBStoreRequest):
    try:
        # Upsert operation: Insert if not exists, otherwise update
        collection.update_one(
            {"_id": request.id},  # Use 'id' as the unique identifier
            {
                "$set": {
                    "messages": request.messages,
                    "chara": request.chara,
                    "model_version": request.model_version
                }
            },
            upsert=True  # Insert the document if it doesn't exist
        )
        return Response()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))