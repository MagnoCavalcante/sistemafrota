# Sistema de Gestão de Frota

Sistema web para gestão de frota desenvolvido com Django.

## Requisitos

- Python 3.11+
- PostgreSQL 15+
- Docker e Docker Compose (opcional)

## Configuração do Ambiente

### Usando Docker (Recomendado)

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/sistemafrota.git
cd sistemafrota
```

2. Copie o arquivo de exemplo de variáveis de ambiente:
```bash
cp .env.example .env
```

3. Edite o arquivo .env com suas configurações

4. Inicie os containers:
```bash
docker-compose up -d
```

O sistema estará disponível em http://localhost:8000

### Instalação Manual

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/sistemafrota.git
cd sistemafrota
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. Execute as migrações:
```bash
python manage.py migrate
```

6. Inicie o servidor:
```bash
python manage.py runserver
```

## Deploy no Render

1. Faça fork do repositório
2. Crie uma nova conta no Render se ainda não tiver
3. Conecte seu repositório GitHub ao Render
4. Crie um novo Web Service
5. Configure as variáveis de ambiente conforme o arquivo .env.example
6. Deploy!

## Estrutura do Projeto

```
sistemafrota/
├── frota/                  # App principal
├── sistemafrota/          # Configurações do projeto
├── templates/             # Templates HTML
├── static/                # Arquivos estáticos
├── media/                 # Arquivos de mídia
├── docker-compose.yml     # Configuração Docker Compose
├── Dockerfile            # Configuração Docker
├── requirements.txt      # Dependências Python
└── README.md            # Este arquivo
```

## Funcionalidades

- Gestão de Veículos
- Gestão de Motoristas
- Controle de Manutenções
- Gestão de Peças
- Relatórios
- Controle de Usuários
- Multi-tenancy

## Contribuindo

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Suporte

Para suporte, envie um email para seu-email@exemplo.com