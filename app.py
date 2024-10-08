import base64
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from groq import Groq
from langchain_core.output_parsers import StrOutputParser
import pyttsx3

load_dotenv()

client = Groq()

def audio_to_text(file_path):
    with open(file_path,"rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=audio_file,
            temperature=0.0
        )
        return transcription.text

def get_ai_response(text):
    llm = ChatGroq(
        model="llama-3.1-8b-instant"
    )
    template = '''
    You are a helpful AI Assistant, you have to answer the user queries.
    User Query: {text}
    Answer:  
    '''
    prompt = PromptTemplate.from_template(template=template)
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"text":text})
    return response

class TextToSpeechEngine:
    def __init__(self):
        self.engine = pyttsx3.init()
    def speak(self, text, play = True, save = False, filename = "output.mp3"):
        if save:
            self.engine.save_to_file(text, filename)
            self.engine.runAndWait()
        if play:
            self.engine.say(text)
            self.engine.runAndWait()

def text_to_audio(text):
    tts_engine = TextToSpeechEngine()
    tts_engine.speak(text, play = False, save = True)

# Text card function
def create_text_card(text, title = "AI Response"):
    card_html = f'''
    <style>
        .card{{
            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
            transition: 0.3s;
            border-radius: 5px;
            padding: 15px;
        }}
        .card:hover{{
            box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
        }}
        .container{{
            padding: 2px 16px;
        }}
    </style>
    <div class = "card">
        <div class = "conatiner">
            <h4><b>{title}</b></h4>
            <p>{text}</p>
        </div>
    </div>
    '''
    st.markdown(card_html, unsafe_allow_html=True)

# Autoplay audio function
def auto_play_audio(audio_file):
    with open(audio_file,"rb") as audio_file:
        audio_bytes = audio_file.read()
    base64_audio = base64.b64encode(audio_bytes).decode("utf-8")
    audio_html = f'<audio src="data:audio/mp3;base64,{base64_audio}" controls autoplay>'
    st.markdown(audio_html, unsafe_allow_html=True)

def main():
    st.set_page_config("Talk To Me")
    st.title("🎤 AI Voice Assistant 🗣️")
    st.write("Click on the recorder to interact with me. How can I assist you today?")
    recorded_audio_file = audio_recorder()
    if recorded_audio_file:
        audio_file = "audio.mp3"
        with open(audio_file,"wb") as f:
            f.write(recorded_audio_file)
        transcribed_text = audio_to_text(audio_file)
        create_text_card(transcribed_text,"Audio Transcription")
        ai_response = get_ai_response(transcribed_text)
        if ai_response:
            cleaned_text = ai_response.replace('*','')
            text_to_audio(cleaned_text)
            file_path = "output.mp3"
            auto_play_audio(file_path)
            st.header("AI Response: ")
            st.write(ai_response)

if __name__ == "__main__":
    main()

# cd "Multilingual AI Assistant"
