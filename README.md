# Sistema de Gerenciamento de Frota

Sistema para gerenciamento de frota, veículos, motoristas, manutenções e relatórios.

## Tecnologias Utilizadas

- Python 3.13
- Django
- PostgreSQL
- Bootstrap 5
- Docker
- Docker Compose

## Funcionalidades

- Gerenciamento de veículos
- Gerenciamento de motoristas
- Controle de manutenções
- Cadastro de peças e serviços
- Gerenciamento de usuários
- Geração de relatórios (PDF e Excel)

## Requisitos

- Docker
- Docker Compose

## Instalação e Execução

1. Clone o repositório:
```bash
git clone https://github.com/SEU_USUARIO/sistemafrota.git
cd sistemafrota
```

2. Inicie os containers:
```bash
docker-compose up -d
```

3. Execute as migrações:
```bash
docker-compose exec web python manage.py migrate
```

4. Crie um superusuário:
```bash
docker-compose exec web python manage.py createsuperuser
```

5. Acesse o sistema em seu navegador:
```
http://localhost:8000
```

## Configuração do Banco de Dados

O projeto está configurado para usar PostgreSQL. As configurações do banco de dados podem ser alteradas no arquivo `docker-compose.yml`.

## Configuração do Ambiente de Desenvolvimento

Para desenvolver localmente sem Docker:

1. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute as migrações:
```bash
python manage.py migrate
```

4. Inicie o servidor de desenvolvimento:
```bash
python manage.py runserver
```

## Estrutura do Projeto

- `frota/`: Aplicação principal
- `sistemafrota/`: Configurações do projeto Django
- `templates/`: Templates HTML
- `static/`: Arquivos estáticos (CSS, JS, imagens)
- `media/`: Arquivos enviados pelos usuários
- `requirements.txt`: Dependências do projeto

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Faça commit das suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Faça push para a branch (`git push origin feature/nova-feature`)
5. Crie um novo Pull Request 