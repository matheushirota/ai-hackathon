import os
from pytube import YouTube
from pytube.exceptions import PytubeError
from fastapi import HTTPException

def download_audio_from_youtube(uri: str):
    try:
        yt = YouTube(uri)
        audio_stream = yt.streams.filter(only_audio=True).first()

        # Obter o caminho absoluto da pasta raiz do projeto
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_file_dir))

        # Combinar o caminho absoluto com o caminho para a pasta temp/temp.wav
        audio_path = os.path.join(project_root, 'temp', 'temp.wav')
        audio_file = audio_stream.download(output_path=os.path.dirname(audio_path), filename='temp.wav')
        return {
            "status": True,
            "path": audio_path
        }
    except PytubeError as pytube_error:
        # Tratar erro do Pytube (por exemplo, URL inválida, vídeo indisponível, etc.)
        raise HTTPException(status_code=400, detail=str(pytube_error))
    except Exception as general_error:
        # Tratar outros erros inesperados
        print(general_error)
        raise HTTPException(status_code=500, detail="Internal server error")
