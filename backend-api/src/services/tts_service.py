import requests
import librosa
from io import BytesIO


class ChatWaifu_TTS(object):
    def __init__(
        self,
    ):
        pass

    def request_multi_line_tts(self, chara, chara_response: str):
        chara_response_ls = chara_response.split("\n")
        responses = [response.split(":")[1].strip() for response in chara_response_ls]
        moratone_list = []
        for response in responses:
            moratone_list.append(
                requests.post(
                    url=self.configs.address.tts_api_url + "/g2p",
                    json={"text": response},
                ).json()
            )
        wav = requests.post(
            url=self.configs.address.tts_api_url + "/multi_synthesis",
            json={
                "lines": responses,
                "model": self.configs.tts_configs.model,
                "modelFile": self.configs.tts_configs.modelFile,
                "speaker": chara,
                "style": chara,
                "moraToneLists": moratone_list,
            },
        )
        wav, _ = librosa.load(BytesIO(wav.content), sr=self.configs.tts_configs.sr)
        return wav

    def request_tts(self, chara, chara_response):
        moratone = requests.post(
            url=self.configs.address.tts_api_url + "/g2p", json={"text": chara_response}
        ).json()
        wav = requests.post(
            url=self.configs.address.tts_api_url + "/synthesis",
            json={
                "text": chara_response,
                "model": self.configs.tts_configs.model,
                "modelFile": self.configs.tts_configs.modelFile,
                "speaker": chara,
                "style": chara,
                "moraToneList": moratone,
            },
        )
        wav, _ = librosa.load(BytesIO(wav.content), sr=self.configs.tts_configs.sr)
        return wav
