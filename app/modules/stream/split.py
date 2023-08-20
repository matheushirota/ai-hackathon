import os
from pydub import AudioSegment

def split_audio_into_chunks(input_audio_path, chunk_size_seconds=120, max_chunk_size_bytes=26214400):
    audio_file_size = os.path.getsize(input_audio_path)
    if audio_file_size > max_chunk_size_bytes:
        song = AudioSegment.from_file(input_audio_path)
        chunk_size = chunk_size_seconds * 1000
        os.makedirs("chunks", exist_ok=True)
        chunk_paths = []
        chunks = [song[i:i+chunk_size] for i in range(0, len(song), chunk_size)]
        for i, chunk in enumerate(chunks):
            chunk_output_path = os.path.join("chunks", f"chunk_{i+1}.wav")
            chunk.export(chunk_output_path, format="wav")
            chunk_paths.append(chunk_output_path)
        return chunk_paths
    else:
        return [input_audio_path]
