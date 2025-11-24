import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from .logger import setup_logger

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()
logger = setup_logger("API_MAIN")

app = FastAPI(
    title="Agente Reembolsos iFood",
    version="1.0.0",
    description="Agente inteligente para suporte a parceiros e clientes sobre reembolsos."
)

PERSIST_DIRECTORY = "./chroma_db"

class RAGService:
    def __init__(self):
        self._chain = None

    def get_chain(self):
        if self._chain is None:
            # inicializa Embeddings e Vector Store
            embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
            vectorstore = Chroma(
                persist_directory=PERSIST_DIRECTORY, 
                embedding_function=embeddings
            )
            
            logger.info("Carregando base vetorial...")

            # busca os 3 fragmentos mais relevantes
            retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

            # temperatura baixa para maior precisão
            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)

            # prompt com as instruções
            template = """
            Você é um assistente virtual especializado em suporte do iFood.
            Sua tarefa é responder perguntas sobre reembolsos, cancelamentos, baseando-se nas políticas da empresa.

            Instruções Estritas:
            1. Baseie-se EXCLUSIVAMENTE no contexto fornecido abaixo.
            2. Se a resposta estiver no contexto, cite a "FONTE/REGRA" mencionada no texto (ex: Política 3.2).
            3. Se a resposta NÃO estiver no contexto, responda APENAS:
               "Não possuo essa resposta no momento, estarei te encaminhando para um atendimento humano".
            4. Mantenha o tom cordial, direto e profissional.

            Contexto recuperado da base de conhecimento:
            {context}

            Pergunta do Usuário:
            {question}
            """
            
            prompt = ChatPromptTemplate.from_template(template)

            self._chain = (
                {"context": retriever, "question": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser()
            )
        return self._chain

rag_service = RAGService()

# schemas
class Interaction(BaseModel):
    question: str

class InteractionResponse(BaseModel):
    answer: str

# endpoints
@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Agente iFood RAG está rodando! Acesse /docs para testar."
    }

@app.post("/api/v1/ask", response_model=InteractionResponse, status_code=200)
async def ask_agent(interaction: Interaction):
    logger.info(f"Recebida nova pergunta: '{interaction.question}'")

    try:
        chain = rag_service.get_chain()
        response = chain.invoke(interaction.question)

        logger.info(f"Resposta gerada com sucesso.")

        return InteractionResponse(answer=response)
    
    except Exception as e:
        logger.error(f"Falha ao processar pergunta: {str(e)}", exc_info=True) 
        raise HTTPException(status_code=500, detail="Erro interno no processamento da IA.")

if __name__ == "__main__":
    # host 0.0.0.0 para acesso externo, ex: Docker/Cloud
    uvicorn.run(app, host="0.0.0.0", port=8000)