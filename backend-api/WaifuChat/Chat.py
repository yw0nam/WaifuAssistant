from openai import OpenAI
from sentence_transformers import SentenceTransformer
import chromadb

class ChatWaifu(object):
    def __init__(self, configs, chara_background):
        self.configs = configs
        self.chara_background = chara_background
        self.dialogue_bra_token = '「'
        self.dialogue_ket_token = '」'
        self.emb_model = SentenceTransformer(self.configs.address.emb_model)
        self.client = OpenAI(
            base_url=self.configs.address.llm_api_url,
            api_key=self.configs.address.llm_api_key,
        )
        self.model_name = self.configs.address.chat_model
        self.load_collection()
        
    def load_collection(self):
        client = chromadb.PersistentClient(path=self.configs.db.db_path)
        self.collection = client.get_collection(self.configs.db.collection_name)
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
        metadatas = self.collection.query(self.emb_model.encode(query).tolist(), where={'target_chara': chara,}, n_results=n_results)
        context_ls = []
        for metadata in metadatas['metadatas'][0]:
            context_ls.append(f"{metadata['context']}\n{metadata['target_chara']}:{metadata['target_sentence']}")
        message = [
            {
                'role' : 'system',
                'content': self.chara_background[chara]
            },
            {
                'content': "Classic scenes for the role are as follows:\n" + "\n###\n".join(context_ls) + self.situation_text + f"ユーザ: {self.dialogue_bra_token}{query}{self.dialogue_ket_token}",
                'role': 'user'
            }
        ]
        return message
    
    def request_completion_with_user_message(self, query, message, generation_configs: dict):
        message.append({
            'role':'user',
            'content': f"ユーザ: {self.dialogue_bra_token}{query}{self.dialogue_ket_token}"
        })
        message = self.request_completion(message, generation_configs)
        return message
    
    def request_completion(self, message, generation_configs: dict):
        """
        This function sends a completion request to the OpenAI API using the provided message and generation configurations.
        It appends the model's response to the message and returns the updated message and the completion object.

        Parameters:
        - message (list): A list of dictionaries representing the conversation. Each dictionary contains 'role' and 'content' keys.
        - generation_configs (dict): A dictionary containing the configuration parameters for the completion request Check OpenAPI official docs https://platform.openai.com/docs/api-reference/chat/create.

        Returns:
        - tuple: A tuple containing the updated message (list) and the completion object.
        """
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=message,
            **generation_configs,
        )
        message.append(completion.choices[0].message.model_dump())
        return message, completion.id