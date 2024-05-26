import os
from dotenv import load_dotenv
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from operator import itemgetter

load_dotenv()

# Set defaults
OPEN_API_KEY = os.getenv("OPEN_API_KEY")
YOUTUBE_VIDEO = "https://www.youtube.com/watch?v=cdiD-9MMpb0"
model = ChatOpenAI(openai_api_key=OPEN_API_KEY, model="gpt-4o")



#output = model.invoke("Name 3 cities in India")

# Chain model output to parser
parser = StrOutputParser()
#chain = model | parser
#print(chain.invoke("Name 3 cities in India."))

# Use prompt templates
template = """
Answer the question based on the context bleow. If you can't answer the question, reply "I don't know!".

Context: {context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
prompt.format(context="Bangalore is situated in the sout of india",question="where is Banagalore located ?")

chain = prompt | model | parser

# model_output = chain.invoke({
#     "context": "Varsha lives in Bangalore",
#     "question": "How is Varsha and Bangalore related to India"
# })
# print(model_output)

#Use translation promt
trnaslation_prompt = ChatPromptTemplate.from_template(
    "Translate {answer} to {language}"
)
trnaslation_chain = (
    {"answer": chain, "language": itemgetter("language")} | trnaslation_prompt | model | parser
)
trans_output = trnaslation_chain.invoke({
    "context": "Varsha lives in Bangalore",
    "question": "How is Varsha and Bangalore related to India?",
    "language": "Malayalam"
})
print(trans_output)





