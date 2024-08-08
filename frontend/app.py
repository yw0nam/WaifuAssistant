import gradio as gr
import requests
import re
api_url = 'http://backend:8001/'

def process(histories: list, query, chara, situation, top_p, temperature):
    prev_message = ""
    if histories != []:
        for history in histories:
            history_user = "ユーザー:" + history[0]
            history_chara = history[1]
            prev_message += history_user + history_chara
    
    res = requests.post(
        url=api_url+'/init_prompt_and_comp',
        json={
            'chara': chara,
            'query': query,
            'situation': situation,
            'history': prev_message,
            'generation_config': {
                'top_p': top_p,
                'temperature': temperature
            },
        }
    ).json()
    print(res)
    wav_res = requests.post(
        url=api_url+'/request_tts',
        json={
            'chara': chara,
            'chara_response': res[-1]['content'].split(':')[1]+ '。'
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
            
        
        chara = gr.Dropdown(
            choices=[
                'ムラサメ', '芦花', '七海', '愛衣', '羽月', 'あやせ', 
                '涼音', '芳乃', 'ナツメ', '茉子', 'レナ', '小春', 
                '栞那', '茉優', '千咲', '希'
            ], 
            value='ムラサメ', 
            label="Character"
        )
        situation = gr.Textbox(value='今は１６時です。', label="Situation")
        top_p_slider = gr.Slider(0.0, 1.0, value=0.3, step=0.01, label="Top-p")
        temperature_slider = gr.Slider(0.0, 2.0, value=0.9, step=0.01, label="Temperature")
        
        audio_output = gr.Audio(label="Audio Response", type="filepath")
        
        def on_send_click(history, query, chara, situation, top_p_slider, temperature_slider):
            return process(history, query, chara, situation, top_p_slider, temperature_slider)
        
        send_button.click(on_send_click, inputs=[chatbot, query, chara, situation, top_p_slider, temperature_slider], outputs=[chatbot, audio_output])
        clear_button.click(clear_history, outputs=[chatbot, audio_output])
    return demo

if __name__ == '__main__':
    ui = create_ui()
    ui.launch(server_port=3000, debug=True)