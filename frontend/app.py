import gradio as gr
import requests

api_url = 'http://backend:8001/'

def fake(query, histories, chara, situation):
    prev_message = ""
    if histories != []:
        for history in histories:
            history[0] = "ユーザー:「" + history[0] + "」"
            prev_message += "\n".join(history)
    
    res = requests.post(
        url=api_url+'/init_prompt_and_comp',
        json={
            'chara': chara,
            'query': query,
            'situation': situation,
            'history': prev_message
        }
    ).json()
    return res[-1]['content'] + '」'

demo = gr.ChatInterface(
    fake, 
    additional_inputs=[
        gr.Textbox(value='ムラサメ', label="You can choose one character to chat: ムラサメ,芦花,七海,愛衣,羽月,あやせ,涼音,芳乃,ナツメ,茉子,レナ,小春,栞那,茉優,千咲,希", ),
        gr.Textbox(value='', label="situation you can set this what you want", )
    ],
)
if __name__ == '__main__':
    demo.launch(server_port=3000, debug=True)