import gradio as gr
import requests
import re
api_url = 'http://backend:8001/'

def process(histories: list, query, chara, situation):
    prev_message = ""
    if histories != []:
        for history in histories:
            history_user = "ユーザー:「" + history[0] + "」"
            history_chara = history[1]
            prev_message += history_user + history_chara
    
    res = requests.post(
        url=api_url+'/init_prompt_and_comp',
        json={
            'chara': chara,
            'query': query,
            'situation': situation,
            'history': prev_message
        }
    ).json()
    wav_res = requests.post(
        url=api_url+'/request_tts',
        json={
            'chara': chara,
            'chara_response': re.sub('「|」', '', res[-1]['content'].split(':')[1])
        }
    )
    audio_filepath = 'response.wav'
    with open(audio_filepath, "wb") as f:
        f.write(wav_res.content)
    
    histories.append((query, res[-1]['content']+'」',))
    return histories, audio_filepath

def clear_history():
    return [], None

def create_ui():
    with gr.Blocks() as demo:
        chatbot = gr.Chatbot(label="Chat with Audio")
        with gr.Row():
            query = gr.Textbox(show_label=False, placeholder="Enter your message")
            send_button = gr.Button("Send")
            clear_button = gr.Button("Clear History")
        
        chara = gr.Textbox(value='ムラサメ', label="Character")
        situation = gr.Textbox(value='', label="Situation")
        
        audio_output = gr.Audio(label="Audio Response", type="filepath")
        
        def on_send_click(history, query, chara, situation):
            return process(history, query, chara, situation)
        
        send_button.click(on_send_click, inputs=[chatbot, query, chara, situation], outputs=[chatbot, audio_output])
        clear_button.click(clear_history, outputs=[chatbot, audio_output])
    return demo

if __name__ == '__main__':
    ui = create_ui()
    ui.launch(server_port=3000, debug=True)