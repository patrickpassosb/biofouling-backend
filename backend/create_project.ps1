# create_project.ps1

# Gera um ID aleatório para o projeto (deve ser único globalmente)
$RANDOM_ID = Get-Random -Minimum 1000 -Maximum 9999
$PROJECT_ID = "biofouling-backend-$RANDOM_ID"
$PROJECT_NAME = "Biofouling Backend"

Write-Host "Criando novo projeto: $PROJECT_NAME (ID: $PROJECT_ID)..." -ForegroundColor Cyan

# Cria o projeto
gcloud projects create $PROJECT_ID --name="$PROJECT_NAME"

if ($LASTEXITCODE -ne 0) {
    Write-Error "Falha ao criar o projeto. Tente novamente ou escolha um ID diferente."
    exit 1
}

Write-Host "Projeto criado com sucesso!" -ForegroundColor Green
Write-Host "Configurando o projeto atual..." -ForegroundColor Cyan

# Define como projeto atual
gcloud config set project $PROJECT_ID

Write-Host "Habilitando APIs necessárias (isso pode levar alguns minutos)..." -ForegroundColor Cyan

# Habilita o faturamento (Billing) - NECESSÁRIO PARA CLOUD RUN
# O usuário precisa vincular uma conta de faturamento manualmente se não tiver uma padrão
Write-Host "IMPORTANTE: Para usar o Cloud Run, você precisa vincular uma conta de faturamento a este projeto." -ForegroundColor Yellow
Write-Host "Vou tentar listar suas contas de faturamento..."

gcloud beta billing accounts list

Write-Host "`nPara vincular, execute: gcloud beta billing projects link $PROJECT_ID --billing-account=ID_DA_CONTA" -ForegroundColor Yellow
Write-Host "Ou faça pelo console: https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID" -ForegroundColor Yellow

# Tenta habilitar os serviços (pode falhar se não tiver billing)
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com

if ($LASTEXITCODE -eq 0) {
    Write-Host "APIs habilitadas!" -ForegroundColor Green
    
    # Atualiza o script de deploy com o novo ID
    (Get-Content deploy.ps1) -replace 'SEU_ID_DO_PROJETO_AQUI', $PROJECT_ID | Set-Content deploy.ps1
    Write-Host "Arquivo deploy.ps1 atualizado com o novo ID: $PROJECT_ID" -ForegroundColor Green
}
else {
    Write-Error "Falha ao habilitar APIs. Verifique se o faturamento está ativado para o projeto."
}
