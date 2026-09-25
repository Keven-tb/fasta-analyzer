# fasta-analyzer

Aplicação Django para upload e análise de arquivos FASTA (formato padrão de
sequências biológicas). Calcula o conteúdo GC (%) e o complemento reverso da
primeira sequência de cada arquivo enviado, orquestrada em três containers
Docker: Django (com Gunicorn), Nginx (proxy reverso) e PostgreSQL.

## Arquitetura

```
Navegador
   │
   ▼
┌─────────────┐      ┌──────────────────┐      ┌─────────────┐
│    nginx    │ ───▶ │  django (gunicorn) │ ───▶ │     db      │
│  proxy      │      │  processa upload   │      │  postgresql │
│  porta 8080 │◀──── │  e serve app       │      │             │
└─────────────┘      └──────────────────┘      └─────────────┘
       │                      │
       └──────────┬───────────┘
                   ▼
         volume nomeado: media-dados
         (arquivos .fasta enviados)
```

- **nginx**: recebe as requisições na porta 8080, repassa para o Django e
  serve diretamente os arquivos estáticos e de mídia (mais eficiente do que
  deixar o Django fazer isso).
- **django**: aplicação principal, rodando com Gunicorn (servidor de
  produção, não o `runserver` de desenvolvimento). Processa o upload,
  calcula %GC e complemento reverso, grava no banco.
- **db**: PostgreSQL, guarda os metadados e resultados de cada análise.

Três volumes nomeados garantem que nada se perde ao destruir os containers:

| Volume           | Usado por      | Guarda                              |
|-------------------|-----------------|--------------------------------------|
| `postgres-dados`  | db              | dados do banco de dados              |
| `media-dados`     | django + nginx  | arquivos `.fasta` enviados           |
| `static-dados`    | django + nginx  | arquivos estáticos coletados         |

## Rotas da aplicação

| Método | Rota          | Descrição                                             |
|--------|---------------|---------------------------------------------------------|
| GET/POST | `/`         | Formulário de upload de arquivo `.fasta`                |
| GET    | `/sequencias/`| Lista todas as sequências já analisadas                 |
| GET    | `/admin/`     | Painel administrativo do Django (requer superusuário)   |

## Variáveis de ambiente

Copie `.env.example` para `.env` e ajuste os valores conforme necessário:

```bash
cp .env.example .env
```

| Variável            | Descrição                                                        |
|----------------------|--------------------------------------------------------------------|
| `DEBUG`              | `True` em desenvolvimento, `False` em produção                     |
| `SECRET_KEY`         | Chave secreta do Django — gere uma própria, nunca reaproveite      |
| `DB_ENGINE`          | `sqlite` (rodar local sem Docker) ou `postgres` (via Docker Compose)|
| `POSTGRES_DB`        | Nome do banco de dados                                             |
| `POSTGRES_USER`      | Usuário do banco                                                   |
| `POSTGRES_PASSWORD`  | Senha do banco                                                     |
| `POSTGRES_HOST`      | `localhost` (local) ou `db` (Docker Compose — nome do serviço)      |
| `POSTGRES_PORT`      | Porta do PostgreSQL (padrão `5432`)                                 |

**Importante:** o arquivo `.env` nunca é versionado (está no `.gitignore`),
pois contém segredos. Apenas `.env.example`, sem valores reais, vai para o
repositório.

## Rodando localmente (sem Docker)

Útil para desenvolvimento rápido, usa SQLite.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# garanta que DB_ENGINE=sqlite no .env

python3 manage.py migrate
python3 manage.py runserver
```

Acesse `http://127.0.0.1:8000/`.

## Rodando com Docker Compose (produção-like)

```bash
cp .env.example .env
# edite o .env com valores reais, se desejar

sudo docker compose up --build
```

Na primeira execução, em outro terminal, rode as migrations dentro do
container (o banco Postgres começa vazio):

```bash
sudo docker compose exec django python manage.py migrate
sudo docker compose exec django python manage.py createsuperuser  # opcional
```

Acesse `http://localhost:8080/`.

Para rodar em segundo plano nas próximas vezes:

```bash
sudo docker compose up -d
```

Para parar (mantendo os volumes, ou seja, mantendo os dados):

```bash
sudo docker compose down
```

## Testando a persistência

Prova de que os dados sobrevivem à destruição dos containers:

```bash
sudo docker compose down
sudo docker volume ls          # os 3 volumes continuam existindo
sudo docker compose up -d
sudo docker compose exec django ls -la /app/media/fastas/   # arquivo continua lá
```

Acesse `http://localhost:8080/sequencias/` — os dados calculados
anteriormente continuam na listagem.

## Estrutura do projeto

```
fasta-analyzer/
├── analyzer/                  # app Django: model, view, forms, templates
│   ├── bio_utils.py            # lógica de parsing FASTA e cálculos
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── admin.py
│   └── templates/analyzer/
├── config/                    # configurações do projeto (settings, urls)
├── nginx/
│   ├── Dockerfile
│   └── nginx.conf
├── Dockerfile                  # imagem própria do Django
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── manage.py
```