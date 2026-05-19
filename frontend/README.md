# Lesson Plan Manager Frontend

SPA em React + Vite para consumir a API Flask do desafio V-Lab.

## Tecnologias

- React
- Vite
- JavaScript
- Axios
- React Router DOM
- CSS simples

## Configuracao

Crie um arquivo `.env` na pasta `frontend`:

```env
VITE_API_URL=http://localhost:5000
```

O backend precisa estar rodando em `http://localhost:5000`.

## Instalar

```bash
npm install
```

## Rodar

```bash
npm run dev
```

## Rotas

- `/`: listagem, filtros, paginacao e exclusao de planos
- `/lesson-plans/new`: cadastro de plano
- `/lesson-plans/:id/edit`: edicao de plano

## Smart Assist

O formulario possui o botao `Gerar Recomendacoes com IA`, que chama:

```text
POST /ai/recommendations
```

As recomendacoes preenchem `contents` e `tags`; `related_topics` sao exibidos apenas na tela.
