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

def summarize_langchain(transcription: str, subject: str, grade: str, mode: str):
    if mode == 1:
        template = """Você é um professor de {subject} que dá aulas para a {grade}, você precisa gerar um resumo de aproximadamente 1 página da sua aula para fornecer um material de estudo para seus alunos, esse resumo deve ser detalhado e passar por todos os pontos abordados na aula e deve ser dividido por tópicos da disciplina. Caso o professor explique pontos específicos da matéria durante a aula, esses pontos devem ser explicados separadamente no resumo.
        conteúdo da aula: 
        "{text}"
        resumo:"""
    elif mode == 2:
        template = """Você é um professor de {subject} que dá aulas para a {grade}, você precisa gerar um resumo de aproximadamente 1 página da sua aula para fornecer um material de estudo para seus alunos, esse resumo deve ser detalhado e passar por todos os pontos abordados na aula e deve ser dividido por tópicos da disciplina. Caso o professor explique pontos específicos da matéria durante a aula, esses pontos devem ser explicados separadamente no resumo. Considere também que os alunos que irão consumir esse resumo possuem o transtorno do déficit de atenção com hiperatividade, sabemos que uns dos pontos de dificuldades desse aluno são: Dificuldade em prestar atenção a detalhes ou errar por descuido em atividades escolares e profissionais, Dificuldade em manter a atenção em tarefas ou atividades lúdicas, Parece não escutar quando falam, Não segue instruções e não termina tarefas escolares, domésticas ou deveres profissionais, Dificuldade em organizar atividades e tarefas, Evita, ou reluta, em envolver-se em tarefas que exijam esforço mental constante, Perde coisas necessárias para tarefas ou atividades, Distrai-se facilmente por estímulo alheios à tarefa, Esquecimento em atividades diárias, Agita as mãos, os pés ou se mexe na cadeira, Abandona a cadeira em sala de aula ou em outras situações nas quais se espera que permaneça sentado, Corre ou escala em demasia em situações nas quais isto é inapropriado, Há dificuldade em brincar ou envolver-se silenciosamente em atividades de lazer, É agitado, como se estivesse com o motor ligado a duzentos por hora, Fala demais, Dá respostas precipitadas antes das perguntas terem sido concluídas, Tem dificuldade em esperar sua vez, Interrompe as pessoas ou intromete-se em assuntos de outros e por isso o texto deve ser adaptado para que ajude o aluno com TDAH entender a aula em questão
        conteúdo da aula: 
        "{text}"
        resumo:"""
    elif mode == 3:
        template = """Você é um professor de {subject} que dá aulas para a {grade}, você precisa gerar um resumo de aproximadamente 1 página da sua aula para fornecer um material de estudo para seus alunos, esse resumo deve ser detalhado e passar por todos os pontos abordados na aula e deve ser dividido por tópicos da disciplina. Caso o professor explique pontos específicos da matéria durante a aula, esses pontos devem ser explicados separadamente no resumo. CConsidere também que os alunos que irão consumir esse resumo possuem o transtorno do espectro autista e por isso o resumo deve ser escrito quando possível de forma lúdica e com exemplos faceis de entender e associar ao contexto que esta sendo utilizado na aula.
        conteúdo da aula: 
        "{text}"
        resumo:"""
    else:
        template = """Você é um professor de {subject} que dá aulas para a {grade}, você precisa gerar um resumo de aproximadamente 1 página da sua aula para fornecer um material de estudo para seus alunos, esse resumo deve ser detalhado e passar por todos os pontos abordados na aula e deve ser dividido por tópicos da disciplina. Caso o professor explique pontos específicos da matéria durante a aula, esses pontos devem ser explicados separadamente no resumo.
        conteúdo da aula: 
        "{text}"
        resumo:"""
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