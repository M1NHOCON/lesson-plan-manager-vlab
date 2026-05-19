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

## Executando com Docker

### Pre-requisitos

- Docker Desktop instalado
- Docker Compose disponivel

### Subir backend e frontend

Na raiz do projeto, execute:

```bash
docker compose up --build
```

Depois acesse:

```text
Frontend: http://localhost:5173
Backend: http://localhost:5000
Swagger: http://localhost:5000/docs/
```

O backend usa SQLite persistido no volume Docker `backend_data`, montado em `/app/instance`. Assim, o banco `lesson_plans.db` continua existindo mesmo se os containers forem recriados.

Por padrao, o Docker Compose usa `LLM_PROVIDER=mock` para facilitar testes locais sem chave de IA. Para usar Gemini ou OpenAI, altere as variaveis no `docker-compose.yml` ou use um arquivo `.env`, mas nunca commite chaves reais.

Se ja existirem containers antigos com os mesmos nomes, pare e remova antes de subir novamente:

```bash
docker stop lesson-plan-backend lesson-plan-frontend
docker rm lesson-plan-backend lesson-plan-frontend
```

Ou, se eles foram criados pelo Compose, execute:

```bash
docker compose down
```

### Parar os containers

```bash
docker compose down
```

### Parar e apagar o volume do SQLite

```bash
docker compose down -v
```

## Próximos passos planejados

1. CRUD de planos de aula.
2. Banco SQLite.
3. Integração com IA.
4. Frontend React.
5. Docker.
6. README final e vídeo de apresentação.
