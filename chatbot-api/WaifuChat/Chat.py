from openai import OpenAI

class ChatWaifu(object):
    def __init__(self, collection, chara_background: dict, emb_model, url, api_key, model_name: str = 'spow12/ChatWaifu_v1.0'):
        self.collection = collection # Chromadb Collection
        self.chara_background = chara_background
        self.emb_model = emb_model
        self.dialogue_bra_token = '「'
        self.dialogue_ket_token = '」'
        self.client = OpenAI(
            base_url=url,
            api_key=api_key,
        )
        self.model_name = model_name
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
    
    def add_user_message_and_request(self, query, message, generation_configs: dict):
        message.append({
            'role':'user',
            'content': f"ユーザ: {self.dialogue_bra_token}{query}{self.dialogue_ket_token}"
        })
        message, completion = self.request_completion(message, generation_configs)
        return message, completion
    
    def request_completion(self, message, generation_configs: dict):
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=message,
            **generation_configs,
        )
        message.append(completion.choices[0].message.model_dump())
        return message, completion