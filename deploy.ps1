# Função para escrever em cores
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-ColorOutput Green "Iniciando deploy do Sistema de Frota..."

# 1. Parar containers existentes
Write-ColorOutput Yellow "Parando containers existentes..."
docker-compose -f docker-compose.prod.yml down

# 2. Remover volumes antigos (opcional - descomente se necessário)
# Write-ColorOutput Yellow "Removendo volumes antigos..."
# docker volume rm sistemafrota_postgres_data sistemafrota_static_volume sistemafrota_media_volume

# 3. Construir as imagens
Write-ColorOutput Yellow "Construindo imagens..."
docker-compose -f docker-compose.prod.yml build

# 4. Iniciar os serviços
Write-ColorOutput Yellow "Iniciando serviços..."
docker-compose -f docker-compose.prod.yml up -d

# 5. Executar migrações
Write-ColorOutput Yellow "Executando migrações..."
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# 6. Coletar arquivos estáticos
Write-ColorOutput Yellow "Coletando arquivos estáticos..."
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# 7. Criar superusuário (se necessário)
Write-ColorOutput Yellow "Deseja criar um superusuário? [Y/N]"
$response = Read-Host
if ($response -eq 'Y' -or $response -eq 'y') {
    docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
}

# 8. Verificar status dos containers
Write-ColorOutput Yellow "Verificando status dos containers..."
docker-compose -f docker-compose.prod.yml ps

# 9. Mostrar logs iniciais
Write-ColorOutput Yellow "Mostrando logs iniciais..."
docker-compose -f docker-compose.prod.yml logs --tail=50

Write-ColorOutput Green "Deploy concluído!"
Write-ColorOutput Green "Acesse: https://frota.mov.pto.br" 