# FastAPI + PostgreSQL

Este documento descreve a integração da aplicação FastAPI com o PostgreSQL utilizando Psycopg 3.

## Objetivo

Permitir que a aplicação executada em `APP01` e `APP02` se conecte ao banco PostgreSQL hospedado no `DB01`.

Arquitetura:

```text
Cliente
   |
   v
PROXY01
   |
   +------> APP01
   |          |
   |          v
   |       FastAPI
   |          |
   |          v
   |       Psycopg
   |          |
   +------> APP02
              |
              v
           FastAPI
              |
              v
           Psycopg
              |
              v
             DB01
          PostgreSQL
```

## Componentes

### FastAPI

Responsável pela aplicação HTTP.

### Psycopg 3

Driver PostgreSQL utilizado pelo Python para estabelecer comunicação com o banco.

Fluxo:

```text
FastAPI
   |
   v
Psycopg
   |
   v
PostgreSQL
```

### PostgreSQL

Executado no:

```text
DB01
10.10.10.30:5432
```

Banco:

```text
linuxinfra
```

Role:

```text
linuxinfra_app
```

## Dependências

O arquivo:

```text
app/requirements.txt
```

passou a conter:

```text
fastapi
uvicorn
psycopg[binary]
```

O pacote:

```text
psycopg[binary]
```

adiciona o driver PostgreSQL utilizado pela aplicação.

## Configuração da aplicação

O `app.py` passou a importar:

```python
import os
import psycopg
```

A conexão é criada por:

```python
def get_db_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
```

As configurações não ficam gravadas diretamente no código.

## Variáveis de ambiente

A aplicação utiliza:

```text
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
```

Nos servidores APP01 e APP02 foi criado um arquivo local:

```text
.env
```

Estrutura:

```text
DB_HOST=10.10.10.30
DB_PORT=5432
DB_NAME=linuxinfra
DB_USER=linuxinfra_app
DB_PASSWORD=<senha>
```

O `.env` não é versionado no Git.

## Proteção do .env

Foi aplicada:

```bash
chmod 600 .env
```

Isso restringe o acesso ao arquivo no sistema operacional.

## Gitignore

O repositório já possui regras para evitar versionamento de arquivos `.env`.

## Dockerignore

Também foi adicionada proteção no `.dockerignore`:

```text
.env
.env.*
```

Isso evita que o arquivo seja enviado ao contexto de build da imagem Docker.

## Imagem da aplicação

A versão anterior era:

```text
linux-infra-app:1.0
```

Depois da integração com Psycopg foi criada:

```text
linux-infra-app:1.1
```

Build:

```bash
sudo docker build -t linux-infra-app:1.1 .
```

## APP01

Container:

```text
app01-api
```

Imagem:

```text
linux-infra-app:1.1
```

Execução:

```bash
sudo docker run -d \
  --name app01-api \
  --hostname app01 \
  --network app-network \
  --env-file .env \
  --restart unless-stopped \
  -p 10.10.10.21:8000:8000 \
  linux-infra-app:1.1
```

## APP02

Container:

```text
app02-api
```

Imagem:

```text
linux-infra-app:1.1
```

Execução:

```bash
sudo docker run -d \
  --name app02-api \
  --hostname app02 \
  --network app-network \
  --env-file .env \
  --restart unless-stopped \
  -p 10.10.10.22:8000:8000 \
  linux-infra-app:1.1
```

## Endpoint principal

APP01:

```bash
curl http://10.10.10.21:8000/
```

Resposta:

```json
{
  "app": "linux-infra-lab",
  "hostname": "app01",
  "status": "ok"
}
```

APP02:

```bash
curl http://10.10.10.22:8000/
```

Resposta:

```json
{
  "app": "linux-infra-lab",
  "hostname": "app02",
  "status": "ok"
}
```

## Health check do banco

Foi criado:

```text
GET /health/db
```

Implementação:

```python
@app.get("/health/db")
def health_db():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()

        return {
            "status": "healthy",
            "database": "connected",
            "hostname": socket.gethostname(),
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        )
```

Esse endpoint executa:

```sql
SELECT 1
```

para validar a comunicação com o PostgreSQL.

## Teste no APP01

```bash
curl http://10.10.10.21:8000/health/db
```

Resultado validado:

```json
{
  "status": "healthy",
  "database": "connected",
  "hostname": "app01"
}
```

## Teste no APP02

```bash
curl http://10.10.10.22:8000/health/db
```

Resultado validado:

```json
{
  "status": "healthy",
  "database": "connected",
  "hostname": "app02"
}
```

## Falha de autenticação durante o teste

Durante a primeira validação do APP01, o endpoint retornou:

```json
{
  "detail": "Database unavailable"
}
```

Foi realizado um teste diretamente dentro do container:

```bash
sudo docker exec app01-api python -c 'import os, psycopg; conn=psycopg.connect(host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], dbname=os.environ["DB_NAME"], user=os.environ["DB_USER"], password=os.environ["DB_PASSWORD"]); print("CONEXAO OK"); conn.close()'
```

O erro identificado foi:

```text
autenticação do tipo senha falhou para o usuário "linuxinfra_app"
```

Isso confirmou que:

- o container alcançava o DB01;
- o PostgreSQL estava respondendo;
- a regra de acesso estava sendo encontrada;
- o problema estava na credencial utilizada pelo container.

Após corrigir a senha no `.env` e recriar o container, o endpoint passou a responder corretamente.

## Importante sobre variáveis de ambiente

Alterar:

```text
.env
```

não modifica automaticamente as variáveis de um container já existente.

O container precisa ser recriado para receber os novos valores.

Fluxo:

```text
alterar .env
     |
     v
parar container
     |
     v
remover container
     |
     v
docker run --env-file .env
     |
     v
novo ambiente
```

## Teste direto do Psycopg

Também foi utilizado:

```bash
sudo docker exec app01-api python -c 'import os, psycopg; conn=psycopg.connect(host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], dbname=os.environ["DB_NAME"], user=os.environ["DB_USER"], password=os.environ["DB_PASSWORD"]); print("CONEXAO OK"); conn.close()'
```

Esse teste é útil para separar:

```text
problema da FastAPI
```

de:

```text
problema do Psycopg / PostgreSQL / credenciais
```

## Fluxo validado

No APP01:

```text
HTTP
 |
 v
FastAPI
 |
 v
Psycopg
 |
 v
PostgreSQL
```

No APP02:

```text
HTTP
 |
 v
FastAPI
 |
 v
Psycopg
 |
 v
PostgreSQL
```

Os dois fluxos foram validados com sucesso.

## Integração com o load balancer

APP01 e APP02 permanecem atrás do PROXY01:

```text
Cliente
   |
   v
PROXY01
   |
   +------> APP01
   |
   +------> APP02
```

Cada backend possui acesso ao mesmo PostgreSQL.

Portanto:

```text
PROXY01
   |
   +------> APP01 ----\
   |                   \
   +------> APP02 ------> DB01
```

## Estado atual

A integração está com:

```text
FastAPI
Psycopg 3
PostgreSQL 17
variáveis de ambiente
Docker
health check do banco
```

APP01:

```text
10.10.10.21:8000
```

APP02:

```text
10.10.10.22:8000
```

DB01:

```text
10.10.10.30:5432
```

## Próximos passos

As próximas etapas da aplicação são:

- criar `GET /records`;
- criar `POST /records`;
- realizar leitura através do PROXY01;
- realizar escrita através do PROXY01;
- provar persistência compartilhada pela API;
- adicionar tratamento de erros;
- avaliar connection pooling;
- avaliar SQLAlchemy;
- avaliar migrations;
- adicionar métricas;
- preparar observabilidade;
- automatizar build e deploy.