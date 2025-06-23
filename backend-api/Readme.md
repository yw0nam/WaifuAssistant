# How to run?

```
uv run uvicorn src.main:app --port 8800 --reload
```

## How to test each modules?

```
uv run python -m src.services.tts_service.streaming_processor
```