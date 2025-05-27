# Sistema de Frota - InstruÃ§Ãµes de Deploy

## Requisitos
- Docker
- Docker Compose
- Git (opcional)

## Passos para Deploy

1. **Configurar o ambiente**
   - Copie o arquivo '.env.example' para '.env'
   - Edite o arquivo '.env' com suas configuraÃ§Ãµes

2. **Configurar o domÃ­nio**
   - Certifique-se que 'frota.mov.pto.br' estÃ¡ apontando para o IP do servidor
   - Ajuste o domÃ­nio no arquivo 'nginx/nginx.conf' se necessÃ¡rio

3. **Executar o deploy**
   Windows:
   `powershell
   .\deploy.ps1
   `
   
   Linux/Mac:
   `ash
   chmod +x deploy.sh
   ./deploy.sh
   `

4. **Verificar a instalaÃ§Ã£o**
   - Acesse https://frota.mov.pto.br
   - Verifique os logs com: 'docker-compose -f docker-compose.prod.yml logs'

## Estrutura de Arquivos
- docker-compose.prod.yml: ConfiguraÃ§Ã£o dos containers
- Dockerfile: ConfiguraÃ§Ã£o da imagem Docker
- .env: VariÃ¡veis de ambiente (criar a partir do .env.example)
- nginx/: ConfiguraÃ§Ãµes do servidor web
- requirements.txt: DependÃªncias Python
- deploy.ps1/deploy.sh: Scripts de deploy

## Backup
O banco de dados Ã© persistido no volume 'postgres_data'.
Recomenda-se fazer backup regular deste volume.

## Suporte
Em caso de problemas, verificar os logs dos containers:
`ash
docker-compose -f docker-compose.prod.yml logs --tail=100
`
