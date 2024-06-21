CUDA_VISIBLE_DEVICES=0 python -m vllm.entrypoints.openai.api_server \
    --model spow12/ChatWaifu_v1.0 \
    --dtype bfloat16 \
    --chat-template ./chat_templates/Vectus-v1.jinja \
    --api-key token-abc123 \
    --max-seq-len-to-capture 128000