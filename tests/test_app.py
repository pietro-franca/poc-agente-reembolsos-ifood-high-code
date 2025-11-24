from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    # verifica se a API sobe 
    response = client.get("/docs")
    assert response.status_code == 200

def test_fallback_message():
    "Testa se o agente recusa perguntas fora do escopo"
    response = client.post("/api/v1/ask", json={"question": """O pedido foi entregue parcialmente, faltando um item. 
                                                O cliente pode solicitar reembolso apenas do item faltante?"""})
    assert response.status_code == 200
    # verifica se a frase de fallback está na resposta
    assert "atendimento humano" in response.json()["answer"]