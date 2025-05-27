# Script PowerShell para enviar a imagem Docker para o Docker Hub

Write-Host "Enviando imagem Docker para o Docker Hub (leonnebarbosa/sistemafrota)" -ForegroundColor Yellow

# Etapa 1: Fazer login no Docker Hub
Write-Host "1. Fazendo login no Docker Hub..." -ForegroundColor Yellow
Write-Host "Por favor, insira suas credenciais do Docker Hub quando solicitado."
docker login

# Verificar se o login foi bem-sucedido
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Falha ao fazer login no Docker Hub. Abortando." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Login realizado com sucesso!" -ForegroundColor Green

# Etapa 2: Construir a imagem Docker
Write-Host "2. Construindo a imagem Docker..." -ForegroundColor Yellow
docker-compose build web

# Verificar se a construção foi bem-sucedida
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Falha ao construir a imagem Docker. Abortando." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Imagem construída com sucesso!" -ForegroundColor Green

# Etapa 3: Enviar a imagem para o Docker Hub
Write-Host "3. Enviando a imagem para o Docker Hub..." -ForegroundColor Yellow
docker push leonnebarbosa/sistemafrota:latest

# Verificar se o envio foi bem-sucedido
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Falha ao enviar a imagem para o Docker Hub. Abortando." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Imagem enviada com sucesso para o Docker Hub!" -ForegroundColor Green

Write-Host "🎉 Processo concluído! A imagem está disponível em: https://hub.docker.com/r/leonnebarbosa/sistemafrota" -ForegroundColor Green

# Pressione qualquer tecla para sair
Write-Host "Pressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 