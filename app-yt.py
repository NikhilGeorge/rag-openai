import tempfile
import whisper
import os
from pytube import YouTube
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
import ssl

# Set defaults
OPEN_API_KEY = os.getenv("OPEN_API_KEY")
YOUTUBE_VIDEO = "https://www.youtube.com/watch?v=cqdm9z3oF0c"
model = ChatOpenAI(openai_api_key=OPEN_API_KEY, model="gpt-4o")

#for resolving the ssl certify verify error for pytube
ssl._create_default_https_context = ssl._create_stdlib_context

def create_transcription():
    if not os.path.exists("transcription.txt"):
        youtube = YouTube(YOUTUBE_VIDEO)
        audio = youtube.streams.filter(only_audio=True).first()

        whisper_model = whisper.load_model("base")

        with tempfile.TemporaryDirectory() as tmpdir:
            file = audio.download(output_path=tmpdir)
            transcription = whisper_model.transcribe(file, fp16=False)["text"].strip()

            with open("transcription.txt", "w") as file:
                file.write(transcription)
        print("Transcription created from youtube video")
    with open("transcription.txt") as file:
        transcription = file.read()
    return transcription


transcription = create_transcription()

parser = StrOutputParser()
template = """
Answer the question based on the context bleow. If you can't answer the question, reply "I don't know!".

Context: {context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
# prompt.format(context="Bangalore is situated in the sout of india",question="where is Banagalore located ?")

chain = prompt | model | parser

# ask questions by passing context
try:
    output = chain.invoke({
        "context": transcription,
        "question": "Who is giving this talk?"
    })
    print(output)
except Exception as e:
    print(e)








