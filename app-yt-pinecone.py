import tempfile
import whisper
import os
from pytube import YouTube
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
import ssl
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_core.runnables import RunnablePassthrough

# Set defaults
OPEN_API_KEY = os.getenv("OPEN_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
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


# load and spit the text
loader = TextLoader("transcription.txt")
text_document = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
splitted_docs = text_splitter.split_documents(text_document)

# Create the embeddings
embeddings = OpenAIEmbeddings()

#connect to pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
pc_index_name = "yt-index"

#connect to index
pc_index = pc.Index(pc_index_name)

#view inde stats
pc_index.describe_index_stats()

#adding the splitted documents to index
# added after this, if we do again ?
#pinecone = PineconeVectorStore.from_documents(splitted_docs, embeddings, index_name=pc_index_name)

#once added to vector store, does just retival work ?
pinecone = PineconeVectorStore(index_name=pc_index_name, embedding=embeddings)

# print(pinecone.similarity_search("Where is this talk happening ?")[:3])

#ask questions by passing context
chain = (
    {"context" : pinecone.as_retriever(), "question": RunnablePassthrough()}
    | prompt
    | model
    | parser
)

try:
    output = chain.invoke("What is the presenter's educational background?")
    print(output)
except Exception as e:
    print(e)








