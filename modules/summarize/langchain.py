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

def summarize_langchain(transcription: str, subject: str, grade: str, has_disability: str):
    template = """Act as a teacher who teaches {subject} for the {grade}, you will receive the audio transcription of a class on the same subject and for the same grade, based on all the points above, write a summary in Brazilian Portuguese about the transcribed class, using a language that is easy to understand for this series, can have several paragraphs, this summary will be used by students as a basis for study, you must return a text in the teacher's view, as if he were writing for the students
    CLASS TRANSCRIPT: 
    "{text}"
    SUMMARY:"""
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