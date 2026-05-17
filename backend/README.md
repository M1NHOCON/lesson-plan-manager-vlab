# Backend

Backend Flask do Sistema de Gerenciamento de Planos de Aula.

## Como rodar localmente

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
python run.py
```

## Rota disponível

```http
GET /health
```

Resposta esperada:

```json
{
  "status": "ok",
  "message": "Lesson Plan Manager API is running"
}
```
