FROM python:3.9
COPY ./requirements.txt ./requirements.txt
RUN apt-get update && apt-get install -y ffmpeg
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
COPY ./app /app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]