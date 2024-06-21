class ChatWaifu(object):
    def __init__(self, collection, chara_background: dict, emb_model):
        self.collection = collection # Chromadb Collection
        self.chara_background = chara_background
        self.emb_model = emb_model
    def init_prompt(self, chara: str, user_query: str, situation: str, n_results: int = 5):
        situation_text = f"""\n\n## Scene Background{situation}\n\nConversation start at here.\n\n"""
        metadatas = self.collection.query(self.emb_model.encode(user_query).tolist(), where={'target_chara': chara,}, n_results=n_results)
        context_ls = []
        for metadata in metadatas['metadatas'][0]:
            context_ls.append(f"{metadata['context']}\n{metadata['target_chara']}:{metadata['target_sentence']}")
        message = [
            {
                'role' : 'system',
                'content': self.chara_background[chara]
            },
            {
                'content': "Classic scenes for the role are as follows:\n" + "\n###\n".join(context_ls) + situation_text + f"ユーザ: 「{user_query}」",
                'role': 'user'
            }
        ]
        return message
    def add_completion_to_message(user_message, message, completion):
        message.append(completion.choices[0].message.dict())
        message.append({
            'role':'user',
            'content': f'{user_message}」'
        })
        return message