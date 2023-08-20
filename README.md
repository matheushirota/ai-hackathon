## Description

This repository contains one of three parts of the project for Hackathon 2023, organized by Quero Educação.

Team: Chutei o Bard

The **ai-hackathon** has been developed using the following technologies:

- Python: Python is a widely-used high-level programming language known for its simplicity and readability. It's commonly used for various purposes, including web development, data analysis, scientific computing, and more.
- FastAPI: FastAPI is a modern and fast web framework for building APIs with Python. It's designed to be easy to use and highly performant, making it a popular choice for developing APIs quickly.
- PyTube: PyTube is a Python library that provides an interface to interact with YouTube. It allows you to download and manipulate YouTube videos using Python code.
- PyDub: PyDub is a Python library for working with audio files. It provides tools for various audio operations, such as converting audio formats, extracting audio segments, and applying effects to audio.
- OpenAI: OpenAI is an artificial intelligence research organization that develops advanced AI models and technologies. It's known for models like GPT (Generative Pre-trained Transformer) that can generate human-like text based on given prompts.
- langchain: It seems like "langchain" might be a custom or internal library or tool related to language processing or translation, but without more context, it's not possible to provide a detailed description.
- AWS RDS MySQL: Amazon Web Services (AWS) Relational Database Service (RDS) is a managed database service. MySQL is a popular open-source relational database management system. AWS RDS MySQL allows you to run and manage MySQL databases in the cloud without the need to handle the underlying infrastructure.
- AWS S3: Amazon Simple Storage Service (S3) is a scalable object storage service offered by AWS. It allows you to store and retrieve large amounts of data, such as files, images, videos, and more, in a highly available and durable manner.
- Boto3: Boto3 is the AWS SDK for Python. It provides an interface to interact with various AWS services using Python code. In your context, it's likely being used to interact with AWS services like S3 to manage files and resources.

## Requirements

To start the project locally, you must first configure the following environment variables:

-> OPENAI_API_KEY (Your API KEY from OpenAI to make calls via api Ex.: sk-00000000000000000000000000000000000000000000000000)
-> RDS_ENDPOINT (Endpoint URL for connecting to a MySQL AWS RDS database)
-> RDS_USERNAME (Database username)
-> RDS_PASSWORD (Database user password)
-> RDS_DATABASE (Database name)
-> AWS_SECRET_KEY (AWS secret key to make calls to s3)
-> AWS_ACCESS_KEY (AWS secret key to make calls to s3)

## Installation of dependencies

The project depends on some libraries, all of which are listed in requirements.txt and you can run this installation using the following command:

```bash
pip install -r requirements.txt
```

Attention, the pydub library needs to have FFMpeg installed in your environment, for that, access the link https://www.ffmpeg.org/ and install it according to your operating system

## Running Locally

To run the project locally it is necessary to start the project with the following command:

```bash
uvicorn app.main:app --reload
```

## Database Modeling

![image](https://github.com/leonakao/hackathon-api/assets/49794183/63a2f92d-f6c0-4054-9cec-6589d389330a)

## API Project Architecture

![image](https://github.com/leonakao/hackathon-api/assets/49794183/41eff641-4b29-4f53-b462-3c1cbaa511c7)

## Project Architecture

![image](https://github.com/leonakao/hackathon-api/assets/49794183/795c410c-badb-4ad7-8ecf-b82cbab0edf0)

Clearly you need Python and PIP installed in your environment

Considering our team's distribution, we decided to separate our project into 3 parts:

Hackathon-front
Hackathon-api
Hackathon-ia
This approach allows us to maintain a fast delivery pace with minimal impact on other contexts.

Another advantage is that, in terms of scaling the project, our IA project requires more resources than our API. Therefore, keeping them separated is advantageous.

## Explanation

- **Hackathon-front** only integrates with Hackathon-api.
- **Hackathon-front** is responsible for all UI and user interactions.
- **Hackathon-api** ensures that all our domain logic is implemented correctly.
- **Hackathon-ia** watches the summary queue (populated by the API) and processes the file to generate a summary PDF.
- **Hackathon-ia** updates the status and links directly in the database once the process is finished.