from openai import OpenAI
# from sentence_transformers import SentenceTransformer
# import chromadb
import requests
from omegaconf import DictConfig
import librosa
from io import BytesIO
class ChatWaifu(object):
    def __init__(self, configs: DictConfig, chara_background: dict, sample_chat: dict):
        self.configs = configs
        self.chara_background = chara_background
        self.sample_chat = sample_chat
        # self.emb_model = SentenceTransformer(self.configs.address.emb_model)
        self.vllm_client = OpenAI(
            base_url=self.configs.address.llm_api_url,
            api_key=self.configs.address.api_key,
        )
        self.model_name = self.configs.address.chat_model
        self.collection = None
        # self.load_collection()
        
    # def load_collection(self):
    #     client = chromadb.PersistentClient(path=self.configs.db.db_path)
    #     self.collection = client.get_collection(self.configs.db.collection_name)
    def init_prompt(self, chara: str, query: str, situation: str = "", n_results: int = 5) -> list:
        """
        Initialize the prompt for the chatbot. This function constructs a prompt with classic scenes for the given character,
        user's query, and situation.

        Parameters:
        - chara (str): The character for which the classic scenes are required.
        - query (str): The user's query.
        - situation (str): The situation in which the chatbot is being used.
        - n_results (int, optional): The number of classic scenes to retrieve. Default is 5.

        Returns:
        - list: A list of dictionaries representing the prompt. Each dictionary contains 'role' and 'content' keys.
        """
        self.situation_text = f"""\n\n## Scene Background{situation}\n\nConversation start at here.\n\n"""
        if self.collection:
            metadatas = self.collection.query(self.emb_model.encode(query).tolist(), where={'target_chara': chara,}, n_results=n_results)
            context_ls = []
            for metadata in metadatas['metadatas'][0]:
                context_ls.append(f"{metadata['context']}\n{metadata['target_chara']}:{metadata['target_sentence']}")
        else:
            context_ls = self.sample_chat[chara]
        message = [
            # {
            #     'role' : 'system',
            #     'content': self.chara_background[chara]
            # },
            {
                'content': f"{self.chara_background[chara]}\nClassic scenes for the role are as follows:\n" + "\n###\n".join(context_ls) + self.situation_text +f"ユーザー: {query}",
                'role': 'user'
            }
        ]
        return message
    
    def request_completion_with_user_message(self, query:str, message:list, generation_configs: dict):
        message.append({
            'role':'user',
            'content': f"ユーザー: {query}"
        })
        message = self.request_completion(message, generation_configs)
        return message
    
    def request_completion(self, message:list, generation_configs: dict):
        """
        This function sends a completion request to the OpenAI API using the provided message and generation configurations.
        It appends the model's response to the message and returns the updated message and the completion object.

        Parameters:
        - message (list): A list of dictionaries representing the conversation. Each dictionary contains 'role' and 'content' keys.
        - generation_configs (dict): A dictionary containing the configuration parameters for the completion request Check OpenAPI official docs https://platform.openai.com/docs/api-reference/chat/create.

        Returns:
        - tuple: A tuple containing the updated message (list) and the completion object.
        """
        completion = self.vllm_client.chat.completions.create(
            model=self.model_name,
            messages=message,
            **generation_configs,
        )
        completion = completion.choices[0].message.model_dump()
        message.append({
            'role': 'assistant',
            'content': completion['content']
        })
        return message
    
    def request_tts(self, chara, chara_response):
        moratone = requests.post(
            url=self.configs.address.tts_api_url + '/g2p',
            json={'text': chara_response}
        ).json()
        wav = requests.post(
            url=self.configs.address.tts_api_url + '/synthesis',
            json={
                'text': chara_response,
                'model': self.configs.tts_configs.model,
                'modelFile': self.configs.tts_configs.modelFile,
                'speaker': chara,
                'style': chara,
                'moraToneList': moratone
            }
        )
        wav, _ = librosa.load(BytesIO(wav.content), sr=self.configs.tts_configs.sr)
        return wav