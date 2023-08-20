import tempfile
import openai
import mysql.connector
from fastapi import FastAPI
from langchain.chat_models import ChatOpenAI
import requests
from app.modules.stream.youtube import download_audio_from_youtube
from app.modules.stream.split import split_audio_into_chunks
from app.modules.transcribe.whisper import transcribe_audio
from app.modules.summarize.langchain import summarize_langchain

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains import SimpleSequentialChain

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from PIL import Image as PILImage
from io import BytesIO

app = FastAPI()

# connection = mysql.connector.connect(
#   host="http://database-bard-api.ctofnlryccp5.us-east-1.rds.amazonaws.com",
#   user="admin",
#   password="ieTk^2aT2X2hA!1IQo$PqA",
#   database="teste"
# )

@app.get('/summarize/youtube')
def youtube(uri: str, category: str, grade: str):
    path_audio = download_audio_from_youtube(uri)
    check_chunk = split_audio_into_chunks(path_audio['path'])
    transcriptions = []
    for i, chunk_path in enumerate(check_chunk):
        if len(check_chunk) > 1:
            try:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                    temp_file_path = temp_file.name
                    chunk_path.export(temp_file_path, format="wav")
                    transcription = transcribe_audio(temp_file_path)
                    transcriptions.append(transcription)
            except Exception as e:
                print(f"Error processing chunk {i+1}: {e}")
        else:
            transcription = transcribe_audio(chunk_path)
            transcriptions.append(transcription)
    merged_transcription = '\n'.join([item['text'] for item in transcriptions])
    summarization = summarize_langchain(merged_transcription, category, grade, 'no')
    
    llm = ChatOpenAI(temperature=.7)
    template = """Você irá receber um texto e deverá extrair o contexto dele, com base nesse contexto você deverá gerar 3 descrições de imagens para esse contexto
    Texto: {text}
    Descrições:
    """
    prompt_template = PromptTemplate(input_variables=["text"], template=template)
    answer_chain = LLMChain(llm=llm, prompt=prompt_template)
    answer = answer_chain.run(summarization)
    prompts = answer.split('\n')
    images = []
    for prompt in prompts:
        if len(prompt) > 1 :
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="512x512",
            )
            image_data = response["data"][0]["url"]
            images.append(image_data)

    output_pdf = "output.pdf"
    doc = SimpleDocTemplate(output_pdf, pagesize=letter)
    story = []

    paragraphs = summarization.split('\n\n')

    for idx, paragraph in enumerate(paragraphs):
        styles = getSampleStyleSheet()
        story.append(Paragraph(paragraph, styles['Normal']))
        story.append(Spacer(1, 15))
        if idx < 3:
            image_data = BytesIO(requests.get(images[idx]).content)
            img = PILImage.open(image_data)
            width, height = img.size
            aspect = height / float(width)
            img_width = 512
            img_height = img_width * aspect
            img = Image(image_data, width=img_width, height=img_height)
            story.append(img)
            story.append(Spacer(1, 5))
    
    doc.build(story)
    print(f"PDF criado com sucesso: {output_pdf}")