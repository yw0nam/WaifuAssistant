# Hugging face spaces (CPU) でエディタ (server_editor.py) のデプロイ用

# See https://huggingface.co/docs/hub/spaces-sdks-docker-first-demo

FROM python:3.10

RUN useradd -m -u 1000 user

USER user

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt $HOME/app

RUN pip install --no-cache-dir -r $HOME/app/requirements.txt

COPY --chown=user . $HOME/app

EXPOSE 7860

# 必要に応じて制限を変更してください
# CMD ["python", "server_editor.py", "--line_length", "50", "--line_count", "3", "--skip_static_files", "--skip_default_models", "--port", "7860"]
CMD ["uvicorn", "server_editor:app", "--host", "0.0.0.0", "--port", "7860"]
