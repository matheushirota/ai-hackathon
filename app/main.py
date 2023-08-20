import tempfile
from fastapi import FastAPI
from app.modules.stream.youtube import download_audio_from_youtube
from app.modules.stream.split import split_audio_into_chunks
from app.modules.transcribe.whisper import transcribe_audio
from app.modules.summarize.langchain import summarize_langchain
app = FastAPI()

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
    return {
        "summarization": summarization
    }