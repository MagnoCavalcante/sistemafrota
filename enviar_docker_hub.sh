#!/bin/bash

# Script para enviar a imagem Docker para o Docker Hub

# Cores para saída no terminal
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Enviando imagem Docker para o Docker Hub (leonnebarbosa/sistemafrota)${NC}"

# Etapa 1: Fazer login no Docker Hub
echo -e "${YELLOW}1. Fazendo login no Docker Hub...${NC}"
echo "Por favor, insira suas credenciais do Docker Hub quando solicitado."
docker login

# Verificar se o login foi bem-sucedido
if [ $? -ne 0 ]; then
    echo "❌ Falha ao fazer login no Docker Hub. Abortando."
    exit 1
fi
echo -e "${GREEN}✅ Login realizado com sucesso!${NC}"

# Etapa 2: Construir a imagem Docker
echo -e "${YELLOW}2. Construindo a imagem Docker...${NC}"
docker-compose build web

# Verificar se a construção foi bem-sucedida
if [ $? -ne 0 ]; then
    echo "❌ Falha ao construir a imagem Docker. Abortando."
    exit 1
fi
echo -e "${GREEN}✅ Imagem construída com sucesso!${NC}"

# Etapa 3: Enviar a imagem para o Docker Hub
echo -e "${YELLOW}3. Enviando a imagem para o Docker Hub...${NC}"
docker push leonnebarbosa/sistemafrota:latest

# Verificar se o envio foi bem-sucedido
if [ $? -ne 0 ]; then
    echo "❌ Falha ao enviar a imagem para o Docker Hub. Abortando."
    exit 1
fi
echo -e "${GREEN}✅ Imagem enviada com sucesso para o Docker Hub!${NC}"

echo -e "${GREEN}🎉 Processo concluído! A imagem está disponível em: https://hub.docker.com/r/leonnebarbosa/sistemafrota${NC}" 