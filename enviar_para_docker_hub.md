# Instruções para enviar o projeto para o Docker Hub

Este documento descreve como enviar a imagem Docker do Sistema de Gerenciamento de Frota para o seu Docker Hub.

## Pré-requisitos

- Docker instalado e configurado
- Docker Compose instalado
- Conta no [Docker Hub](https://hub.docker.com/)

## Passo a Passo

### 1. Fazer login no Docker Hub

```bash
# No terminal (Windows, Linux ou macOS)
docker login
```

Insira seu nome de usuário e senha do Docker Hub quando solicitado.

### 2. Construir a imagem com a tag correta

```bash
# No terminal
docker-compose build web
```

Isso vai construir a imagem com a tag `leonnebarbosa/sistemafrota:latest` conforme configurado no docker-compose.yml.

### 3. Enviar a imagem para o Docker Hub

```bash
# No terminal
docker push leonnebarbosa/sistemafrota:latest
```

Aguarde até que o upload seja concluído. Isso pode levar alguns minutos dependendo da sua conexão de internet.

### 4. Verificar no Docker Hub

Após o envio, acesse sua conta no Docker Hub através do link:
https://hub.docker.com/repositories/leonnebarbosa

Você deve ver o repositório `sistemafrota` com a tag `latest`.

## Para usuários do Windows (PowerShell)

Se estiver usando o PowerShell no Windows, você pode executar todos os comandos de uma vez:

```powershell
# Fazer login no Docker Hub
docker login

# Construir a imagem
docker-compose build web

# Enviar a imagem para o Docker Hub
docker push leonnebarbosa/sistemafrota:latest
```

## Usando o script automatizado (Linux/macOS)

Também criamos um script para facilitar esse processo. Para utilizá-lo:

1. Dê permissão de execução ao script:
```bash
chmod +x enviar_docker_hub.sh
```

2. Execute o script:
```bash
./enviar_docker_hub.sh
```

## Como usar a imagem depois de publicada

Após a publicação da imagem, qualquer pessoa pode utilizá-la com o seguinte comando:

```bash
docker pull leonnebarbosa/sistemafrota:latest
```

Para executar a aplicação usando a imagem publicada:

```bash
docker-compose up -d
``` 