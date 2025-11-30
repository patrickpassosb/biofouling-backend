# deploy.ps1

# Nome do serviço no Cloud Run
$SERVICE_NAME = "biofouling-api"
# Região do Google Cloud
$REGION = "us-central1"
# ID do Projeto no Google Cloud (DEFINA O SEU AQUI)
$PROJECT_ID = "biofouling-backend-6776" 

Write-Host "Iniciando deploy do serviço $SERVICE_NAME no projeto $PROJECT_ID..." -ForegroundColor Cyan

# Verifica se o gcloud está instalado
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Error "O Google Cloud CLI (gcloud) não foi encontrado. Por favor, instale-o e faça login antes de continuar."
    exit 1
}

# Define o projeto atual
gcloud config set project $PROJECT_ID

# Determine the project root (parent of scripts directory)
$ScriptRoot = Split-Path $MyInvocation.MyCommand.Path
$SourcePath = Resolve-Path (Join-Path $ScriptRoot "..")

# Read API key from .env file if it exists
$EnvFile = Join-Path $SourcePath ".env"
$ApiKey = ""
if (Test-Path $EnvFile) {
    $envContent = Get-Content $EnvFile -Raw
    if ($envContent -match 'EXTERNAL_MODEL_API_KEY=(.+)') {
        $ApiKey = $matches[1].Trim()
        Write-Host "✅ API Key encontrada no .env" -ForegroundColor Green
    }
}

# Comando de deploy
if ($ApiKey) {
    gcloud run deploy $SERVICE_NAME `
        --source $SourcePath `
        --region $REGION `
        --project $PROJECT_ID `
        --allow-unauthenticated `
        --set-env-vars "EXTERNAL_MODEL_API_KEY=$ApiKey"
}
else {
    Write-Host "⚠️  API Key não encontrada. Deploy sem variável de ambiente." -ForegroundColor Yellow
    gcloud run deploy $SERVICE_NAME `
        --source $SourcePath `
        --region $REGION `
        --project $PROJECT_ID `
        --allow-unauthenticated
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Deploy concluído com sucesso!" -ForegroundColor Green
}
else {
    Write-Host "`n❌ Falha no deploy. Verifique os erros acima." -ForegroundColor Red
}
