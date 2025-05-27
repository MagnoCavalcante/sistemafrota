# Instruções para subir o projeto no GitHub

Siga os passos abaixo para inicializar o repositório Git e subir o projeto no GitHub:

## 1. Inicializar o repositório Git local

```bash
# Inicializar repositório Git
git init

# Adicionar todos os arquivos
git add .

# Criar o primeiro commit
git commit -m "Versão inicial do Sistema de Gerenciamento de Frota"
```

## 2. Criar o repositório no GitHub

1. Acesse [GitHub](https://github.com/) e faça login na sua conta
2. Clique no botão "+" no canto superior direito e selecione "New repository"
3. Preencha:
   - Nome do repositório: `sistemafrota`
   - Descrição: `Sistema de Gerenciamento de Frota desenvolvido em Django`
   - Visibilidade: Public ou Private (conforme sua preferência)
4. Não inicialize o repositório com README, .gitignore ou License
5. Clique em "Create repository"

## 3. Conectar o repositório local ao GitHub e enviar os arquivos

```bash
# Adicionar o repositório remoto (substitua SEU_USUARIO pelo seu nome de usuário GitHub)
git remote add origin https://github.com/SEU_USUARIO/sistemafrota.git

# Enviar o código para o GitHub
git push -u origin master
```

Se estiver usando a autenticação de dois fatores no GitHub, você pode precisar:
- Criar um token de acesso pessoal em GitHub → Settings → Developer settings → Personal access tokens
- Usar esse token como senha quando solicitado durante o push

## 4. Verificar o repositório no GitHub

Acesse `https://github.com/SEU_USUARIO/sistemafrota` para confirmar que todos os arquivos foram enviados corretamente.

## 5. Comandos úteis para atualizações futuras

```bash
# Verificar status do repositório
git status

# Adicionar alterações
git add .

# Criar novo commit
git commit -m "Descrição das alterações"

# Enviar para o GitHub
git push
``` 