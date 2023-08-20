import tempfile
import openai
from fastapi import FastAPI
from langchain.chat_models import ChatOpenAI
import pymysql
import requests
from app.modules.stream.youtube import download_audio_from_youtube
from app.modules.stream.split import split_audio_into_chunks
from app.modules.transcribe.whisper import transcribe_audio
from app.modules.summarize.langchain import summarize_langchain
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from PIL import Image as PILImage
from io import BytesIO
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)
import boto3
from botocore.exceptions import NoCredentialsError
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

app = FastAPI()

connection = pymysql.connect(
    host=os.environ["RDS_ENDPOINT"],
    port=3306,
    user=os.environ["RDS_USERNAME"],
    password=os.environ["RDS_PASSWORD"],
    database=os.environ["RDS_DATABASE"],
)
cursor = connection.cursor(pymysql.cursors.DictCursor)

def exec_queue():
    cursor.execute('SELECT * FROM summary_queues WHERE status != "DONE" AND retries < 3 ORDER BY created_at DESC LIMIT 1')
    results = cursor.fetchall()
    print(results)
    if not results:
        return
    for result in results:
        try:
            query_update_status = 'UPDATE summary_queues SET status = "{status}", retries = {retries} WHERE id = "{summary_id}"'
            query_formated = query_update_status.format(status="PROCESSING", retries=int(result['retries']) + 1, summary_id=result['id'])
            cursor.execute(query_formated)
            connection.commit()
        except Exception as e:
            print("Exeception occured:{}".format(e))
        
        query_get_file_input = 'SELECT * FROM file_inputs WHERE summary_id = "{summary_id}"'
        query_file_input_formatted = query_get_file_input.format(summary_id=result['summary_id'])
        cursor.execute(query_file_input_formatted)
        file_inputs = cursor.fetchall()
        for file in file_inputs:
            if file['type'] == 'LINK':
                query_get_profiles = 'SELECT * FROM profiles WHERE summary_id = "{summary_id}"'
                query_get_profiles_formatted = query_get_profiles.format(summary_id=result['summary_id'])
                cursor.execute(query_get_profiles_formatted)
                profiles = cursor.fetchall()
                for profile in profiles:
                    link = file['public_url']
                    category = profile['subject']
                    grade = profile['grade']
                    mode = profile['mode']
                    summary_id = result['summary_id']

                    query_get_summaries = 'SELECT * FROM summaries WHERE id = "{summary_id}"'
                    query_get_summaries_formatted = query_get_summaries.format(summary_id=result['summary_id'])
                    cursor.execute(query_get_summaries_formatted)
                    summaries = cursor.fetchall()
                    for summary in summaries:
                        summary_title = summary['title']
                        youtube(link, category, grade, summary_id, mode, summary_title)
                        return
            else:
                return

def youtube(uri: str, category: str, grade: str, summary_id: str, mode: str, summary_title: str):
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
    summarization = summarize_langchain(merged_transcription, category, grade, mode)
    
    llm = ChatOpenAI(temperature=.7)
    template = """Você irá receber um texto e deverá extrair o contexto dele, com base nesse contexto você deverá gerar 3 descrições de imagens para esse contexto, as 3 descrições não podem conter temas probidos pela OpenAI em prompts
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

    output_pdf = "temp_output.pdf"
    doc = SimpleDocTemplate(output_pdf, pagesize=letter)
    story = []

    paragraphs = summarization.split('\n\n')

    bard_style_text = ParagraphStyle(
        "bard_style_text",
        parent=getSampleStyleSheet()["Normal"],
        fontSize=14,
        leading=24
    )

    bard_style_title = ParagraphStyle(
        "bard_style_title",
        parent=getSampleStyleSheet()["Normal"],
        fontSize=18,
        leading=28,
        textColor="#3498DB"
    )

    story.append(Paragraph(summary_title, bard_style_title))
    story.append(Spacer(1, 10))
    for idx, paragraph in enumerate(paragraphs):
        story.append(Paragraph(paragraph, bard_style_text))
        story.append(Spacer(1, 5))
        if idx < 3:
            image_data = BytesIO(requests.get(images[idx]).content)
            img = PILImage.open(image_data)
            width, height = img.size
            aspect = height / float(width)
            img_width = 455
            img_height = img_width * aspect
            img = Image(image_data, width=img_width, height=img_height)
            story.append(img)
            story.append(Spacer(1, 5))
    
    doc.build(story)
    upload_to_aws(output_pdf, 'bard-ai-bucket', summary_id + '.pdf', summary_id)

def upload_to_aws(local_file: str, bucket: str, s3_file: str, summary_id: str):
    s3 = boto3.client('s3', aws_access_key_id=os.environ["AWS_ACCESS_KEY"], aws_secret_access_key=os.environ["AWS_SECRET_KEY"])
    try:
        upload = s3.upload_file(local_file, bucket, s3_file)
        try:
            query_update_status = 'UPDATE summary_queues SET status = "{status}" WHERE summary_id = "{summary_id}"'
            query_formated = query_update_status.format(status="DONE", summary_id=summary_id)
            cursor.execute(query_formated)
            connection.commit()
            query_update_summaries = 'UPDATE summaries SET status = "{status}", file_path = "{file_path}" WHERE id = "{summary_id}"'
            s3Uri = "https://bard-ai-bucket.s3.amazonaws.com/" + s3_file
            query_summaries_formated = query_update_summaries.format(status="done", file_path=s3Uri, summary_id=summary_id)
            cursor.execute(query_summaries_formated)
            connection.commit()
            return True
        except Exception as e:
            print("Exeception occured:{}".format(e))
            return False
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

scheduler = BackgroundScheduler()
scheduler.add_job(exec_queue, trigger=CronTrigger(second='0'))
scheduler.start()