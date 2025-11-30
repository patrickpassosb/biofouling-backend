# Biofouling Prediction Backend

Backend service for the Transpetro Hackathon Biofouling Prediction project. This API serves a Machine Learning model to predict biofouling levels on ships based on voyage data.

## Features

- **FastAPI**: High-performance, easy-to-learn, fast to code, ready for production.
- **Machine Learning**: Serves Scikit-learn/XGBoost models.
- **Dockerized**: Ready for deployment on Google Cloud Run.
- **UV**: Fast Python package installer and resolver.

## Project Structure

```
backend/
├── app/
│   ├── api/            # API endpoints
│   ├── core/           # Core logic (config, model loader)
│   ├── models/         # Pydantic models
│   ├── ml_model/       # Trained ML models
│   └── main.py         # App entry point
├── pyproject.toml      # Dependencies
├── Dockerfile          # Docker configuration
└── train_mock_model.py # Script to generate a mock model (for testing)
```

## Local Development

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (Recommended)

### Setup

1.  **Install dependencies**:
    ```bash
    uv sync
    ```

2.  **Generate Mock Model** (if you don't have the real one):
    ```bash
    uv run python train_mock_model.py
    ```

3.  **Run the server**:
    ```bash
    uv run uvicorn app.main:app --reload
    ```

4.  **Access API Documentation**:
    Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.

## Docker Build & Run

1.  **Build the image**:
    ```bash
    docker build -t biofouling-api .
    ```

2.  **Run the container**:
    ```bash
    docker run -p 8080:8080 biofouling-api
    ```

## Deployment (Google Cloud Run)

1.  **Deploy**:
    ```bash
    gcloud run deploy biofouling-api \
      --source . \
      --region us-central1 \
      --allow-unauthenticated
    ```

## API Endpoints

-   `GET /health`: Check service health.
-   `POST /api/v1/predict`: Predict biofouling for a single voyage.
-   `POST /api/v1/predict/batch`: Predict biofouling for multiple voyages.
-   `GET /api/v1/model/info`: Get loaded model information.
