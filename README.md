# Lesson Plan Manager V-Lab

Sistema de Gerenciamento de Planos de Aula desenvolvido para o desafio técnico do V-Lab.

## Objetivo

Criar uma aplicação para gerenciar planos de aula, com backend Flask, frontend SPA, persistência em banco de dados e integração futura com IA/LLM.

## Stack escolhida

- Backend: Python + Flask
- API: Flask Blueprints
- Configuração: python-dotenv
- Validação futura: Pydantic
- Frontend planejado: React + Vite
- Banco planejado: SQLite
- Containerização planejada: Docker

## Estrutura de pastas

```text
lesson-plan-manager-vlab/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── utils/
│   ├── run.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
├── frontend/
├── docker/
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Como rodar o backend localmente

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
python run.py
```

Depois acesse:

```text
http://localhost:5000/health
```

## Próximos passos planejados

1. CRUD de planos de aula.
2. Banco SQLite.
3. Integração com IA.
4. Frontend React.
5. Docker.
6. README final e vídeo de apresentação.
