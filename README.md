# Backend de Predição de Biofouling

> **Nota**: Este README está em português porque o projeto foi desenvolvido para o Hackathon da Transpetro, um evento brasileiro.

Backend para o projeto de Predição de Biofouling do Hackathon Transpetro. Esta API atua como proxy e camada de transformação de dados para um modelo de ML externo que prediz níveis de biofouling em navios baseado em dados de viagem.

## Funcionalidades

- **FastAPI**: Framework web moderno, rápido e de alta performance
- **Integração com API Externa**: Conecta-se a serviço externo de predição ML
- **Dockerizado**: Pronto para deployment no Google Cloud Run
- **UV**: Instalador e resolvedor de pacotes Python ultrarrápido
- **CORS Configurado**: Pronto para integração com frontend
- **Testes Abrangentes**: Testes automatizados de API incluídos

## Estrutura do Projeto

```
biofouling-backend/
├── .gitignore              # Regras do Git
├── README.md               # Este arquivo
├── docs/                   # Documentação e contexto
│   ├── context.md
│   ├── hackathon.ipynb
│   └── regulamento-transpetro.md
└── backend/
    ├── .dockerignore       # Regras do Docker
    ├── .env.example        # Template de variáveis de ambiente
    ├── Dockerfile          # Configuração Docker
    ├── pyproject.toml      # Dependências (uv)
    ├── uv.lock            # Dependências travadas
    ├── app/
    │   ├── main.py         # Ponto de entrada da aplicação FastAPI
    │   ├── api/
    │   │   └── routes/     # Endpoints da API
    │   │       ├── health.py
    │   │       └── predictions.py
    │   ├── core/           # Lógica central
    │   │   ├── config.py   # Gerenciamento de configuração
    │   │   └── model_loader.py  # Cliente da API externa
    │   └── models/         # Schemas Pydantic
    │       └── schemas.py
    ├── scripts/            # Scripts de deployment e utilitários
    │   └── deploy.ps1      # Script de deployment Google Cloud Run
    └── tests/              # Suite de testes
        └── test_api.py     # Testes de integração da API
```

## Desenvolvimento Local

### Pré-requisitos

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (Recomendado)

### Configuração

1. **Clone o repositório**:
   ```bash
   git clone <repository-url>
   cd biofouling-backend/backend
   ```

2. **Instale as dependências**:
   ```bash
   uv sync
   ```

3. **Configure as variáveis de ambiente**:
   ```bash
   cp .env.example .env
   # Edite o .env e adicione sua EXTERNAL_MODEL_API_KEY
   ```

4. **Execute o servidor**:
   ```bash
   uv run uvicorn app.main:app --reload
   ```

5. **Acesse a documentação da API**:
   Abra [http://localhost:8000/docs](http://localhost:8000/docs) no seu navegador.

### Executando os Testes

```bash
cd backend
uv run python tests/test_api.py
```

## Build e Execução com Docker

1. **Build da imagem**:
   ```bash
   cd backend
   docker build -t biofouling-api .
   ```

2. **Execute o container**:
   ```bash
   docker run -p 8080:8080 \
     -e EXTERNAL_MODEL_API_KEY=sua_api_key_aqui \
     biofouling-api
   ```

## Deployment (Google Cloud Run)

### Usando o Script de Deploy (Recomendado)

1. **Navegue até o diretório de scripts**:
   ```bash
   cd backend/scripts
   ```

2. **Execute o script de deployment**:
   ```powershell
   .\deploy.ps1
   ```

O script automaticamente:
- Lê a API key do arquivo `.env`
- Faz deploy no Google Cloud Run
- Configura as variáveis de ambiente

### Deployment Manual

```bash
cd backend
gcloud run deploy biofouling-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "EXTERNAL_MODEL_API_KEY=sua_api_key_aqui"
```

## Endpoints da API

- `GET /health`: Verifica a saúde do serviço e status de configuração do modelo
- `POST /api/v1/predict`: Prediz biofouling para uma única viagem
- `POST /api/v1/predict/batch`: Prediz biofouling para múltiplas viagens
- `GET /api/v1/model/info`: Obtém informações do modelo externo

### Exemplo de Requisição

```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "shipName": "NAVIO-123",
    "speed": 12.0,
    "duration": 15.5,
    "distance": 4500.0,
    "beaufortScale": 3,
    "Area_Molhada": 500.0,
    "MASSA_TOTAL_TON": 50000.0,
    "TIPO_COMBUSTIVEL_PRINCIPAL": "HFO",
    "decLatitude": -23.0,
    "decLongitude": -43.0,
    "DiasDesdeUltimaLimpeza": 180.0
  }'
```

### Exemplo de Resposta

```json
{
  "ship_id": "NAVIO-123",
  "biofouling_level": 2,
  "risk_category": "High",
  "recommended_action": "Schedule cleaning within 1 month",
  "estimated_fuel_impact": 15.0,
  "confidence_score": 0.85,
  "timestamp": "2025-11-30T17:30:00Z"
}
```

## Variáveis de Ambiente

| Variável | Descrição | Obrigatória | Padrão |
|----------|-----------|-------------|--------|
| `EXTERNAL_MODEL_URL` | URL da API ML externa | Não | `https://carpenterbb-api-transpetro-hackathon.hf.space/predict` |
| `EXTERNAL_MODEL_API_KEY` | Chave de API para o serviço externo | Sim | - |
| `LOG_LEVEL` | Nível de logging | Não | `INFO` |
| `API_V1_STR` | Prefixo da versão da API | Não | `/api/v1` |

## Configuração de CORS

A API está configurada para aceitar requisições de:
- `http://localhost:3000` (desenvolvimento local do frontend)
- `https://biofouling-frontend.vercel.app` (frontend em produção)

Para adicionar mais origens, edite `backend/app/main.py`.

## Stack Tecnológica

- **FastAPI**: Framework web moderno e rápido
- **Pydantic**: Validação de dados usando type annotations do Python
- **httpx**: Cliente HTTP assíncrono para chamadas à API externa
- **uvicorn**: Servidor ASGI
- **Docker**: Containerização
- **Google Cloud Run**: Plataforma de deployment serverless

## Licença

Este projeto foi desenvolvido para o Hackathon da Transpetro.
