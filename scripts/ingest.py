import pandas as pd
from dotenv import load_dotenv
from app.logger import setup_logger

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

load_dotenv()
logger = setup_logger("INGEST_DATA")

def ingest_data(csv_path: str, persist_directory: str):
    logger.info(f"Processando base de conhecimento: {csv_path}")
    
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"CSV carregado. Total de linhas: {len(df)}")
    except Exception as e:
        logger.critical(f"Erro fatal ao ler CSV: {e}")
        return

    documents = []
    for _, row in df.iterrows():
        # formatação para análise de contexto pelo LLM
        content = (
            f"CATEGORIA: {row['categoria']}\n"
            f"PERGUNTA: {row['pergunta']}\n"
            f"RESPOSTA DA POLÍTICA: {row['resposta']}\n"
            f"FONTE/REGRA: {row['fonte']}"
        )
        
        # metadados para recuperação futura se necessário
        metadata = {
            "source": row['fonte'],
            "category": row['categoria']
        }
        
        documents.append(Document(page_content=content, metadata=metadata))

    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

    if documents:
        # cria/atualiza o banco vetorial
        Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=persist_directory
        )
        logger.info(f"Sucesso! {len(documents)} regras de negócio indexadas")
    else:
        logger.warning("Nenhum documento foi gerado a partir do CSV")

if __name__ == "__main__":
    ingest_data(csv_path="base_conhecimento_ifood_genai-exemplo.csv", persist_directory="./chroma_db")