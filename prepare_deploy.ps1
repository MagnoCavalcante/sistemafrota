# Criar pasta de deploy
$deployFolder = "deploy_sistemafrota"
New-Item -ItemType Directory -Force -Path $deployFolder

# Copiar arquivos necessários
Copy-Item "docker-compose.prod.yml" -Destination "$deployFolder/"
Copy-Item "Dockerfile.prod" -Destination "$deployFolder/Dockerfile"
Copy-Item "requirements.txt" -Destination "$deployFolder/"
Copy-Item "manage.py" -Destination "$deployFolder/"
Copy-Item "deploy.ps1" -Destination "$deployFolder/"
Copy-Item "deploy.sh" -Destination "$deployFolder/"
Copy-Item -Recurse "frota" -Destination "$deployFolder/"
Copy-Item -Recurse "sistemafrota" -Destination "$deployFolder/"
Copy-Item -Recurse "static" -Destination "$deployFolder/"
Copy-Item -Recurse "nginx" -Destination "$deployFolder/"

# Criar arquivo .env de exemplo
$envContent = @"
# Configurações do Django
DEBUG=False
SECRET_KEY=sua_chave_secreta_aqui
ALLOWED_HOSTS=frota.mov.pto.br,localhost,127.0.0.1

# Configurações do Banco de Dados PostgreSQL
POSTGRES_DB=sistemafrota
POSTGRES_USER=seu_usuario
POSTGRES_PASSWORD=sua_senha_segura
DATABASE_URL=postgres://seu_usuario:sua_senha_segura@db:5432/sistemafrota

# Configurações de Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu_email@gmail.com
EMAIL_HOST_PASSWORD=sua_senha_de_app

# Configurações de Segurança
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
"@

$envContent | Out-File -FilePath "$deployFolder/.env.example" -Encoding UTF8

# Criar arquivo README com instruções
$readmeContent = @"
# Sistema de Frota - Instruções de Deploy

## Requisitos
- Docker
- Docker Compose
- Git (opcional)

## Passos para Deploy

1. **Configurar o ambiente**
   - Copie o arquivo '.env.example' para '.env'
   - Edite o arquivo '.env' com suas configurações

2. **Configurar o domínio**
   - Certifique-se que 'frota.mov.pto.br' está apontando para o IP do servidor
   - Ajuste o domínio no arquivo 'nginx/nginx.conf' se necessário

3. **Executar o deploy**
   Windows:
   ```powershell
   .\deploy.ps1
   ```
   
   Linux/Mac:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

4. **Verificar a instalação**
   - Acesse https://frota.mov.pto.br
   - Verifique os logs com: 'docker-compose -f docker-compose.prod.yml logs'

## Estrutura de Arquivos
- docker-compose.prod.yml: Configuração dos containers
- Dockerfile: Configuração da imagem Docker
- .env: Variáveis de ambiente (criar a partir do .env.example)
- nginx/: Configurações do servidor web
- requirements.txt: Dependências Python
- deploy.ps1/deploy.sh: Scripts de deploy

## Backup
O banco de dados é persistido no volume 'postgres_data'.
Recomenda-se fazer backup regular deste volume.

## Suporte
Em caso de problemas, verificar os logs dos containers:
```bash
docker-compose -f docker-compose.prod.yml logs --tail=100
```
"@

$readmeContent | Out-File -FilePath "$deployFolder/README.md" -Encoding UTF8

Write-Output "Pasta de deploy criada em: $deployFolder"
Write-Output "Por favor, revise os arquivos antes de transferir para o servidor de produção." 