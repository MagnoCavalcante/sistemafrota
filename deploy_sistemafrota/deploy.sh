#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Iniciando deploy do Sistema de Frota...${NC}"

# 1. Parar containers existentes
echo -e "${YELLOW}Parando containers existentes...${NC}"
docker-compose -f docker-compose.prod.yml down

# 2. Remover volumes antigos (opcional - descomente se necessário)
# echo -e "${YELLOW}Removendo volumes antigos...${NC}"
# docker volume rm sistemafrota_postgres_data sistemafrota_static_volume sistemafrota_media_volume

# 3. Construir as imagens
echo -e "${YELLOW}Construindo imagens...${NC}"
docker-compose -f docker-compose.prod.yml build

# 4. Iniciar os serviços
echo -e "${YELLOW}Iniciando serviços...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# 5. Executar migrações
echo -e "${YELLOW}Executando migrações...${NC}"
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# 6. Coletar arquivos estáticos
echo -e "${YELLOW}Coletando arquivos estáticos...${NC}"
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# 7. Criar superusuário (se necessário)
echo -e "${YELLOW}Deseja criar um superusuário? [y/N]${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])+$ ]]
then
    docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
fi

# 8. Verificar status dos containers
echo -e "${YELLOW}Verificando status dos containers...${NC}"
docker-compose -f docker-compose.prod.yml ps

# 9. Mostrar logs iniciais
echo -e "${YELLOW}Mostrando logs iniciais...${NC}"
docker-compose -f docker-compose.prod.yml logs --tail=50

echo -e "${GREEN}Deploy concluído!${NC}"
echo -e "${GREEN}Acesse: https://frota.mov.pto.br${NC}" 