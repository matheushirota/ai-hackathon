import openai
from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)
openai.api_key = os.environ["OPENAI_API_KEY"]

def summarize_langchain(transcription: str, subject: str, grade: str, has_disability: str):
    template = """You are a {subject} teacher who teaches classes for the {grade}, you recorded the audio of your class and now you need to provide a summary of the recording of that class to provide study material for your students, this summary should be very detailed going through all the points addressed in the class and must be divided by subject topics, if the teacher explains specific points of the subject during the class, these points must be explained separately in the summary without omitting the explanation of each point in addition your summary must be done in Brazilian Portuguese
    recorded class transcript: 
    "{text}"
    summary:"""
    text_placeholder = "{text}"
    formated_template = template.format(subject=subject, grade=grade, text=text_placeholder)
    prompt = PromptTemplate.from_template(formated_template)
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
    llm_chain = LLMChain(llm=llm, prompt=prompt)    
    stuff_chain = StuffDocumentsChain(
        llm_chain=llm_chain, document_variable_name="text"
    )
    doc = Document(page_content=transcription, metadata={})
    return stuff_chain.run([doc])