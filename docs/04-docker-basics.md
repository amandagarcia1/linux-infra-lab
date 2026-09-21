# Docker no laboratório

Este documento registra a instalação, os primeiros testes e a evolução do uso de Docker no `linux-infra-lab`.

## Objetivo

Utilizar Docker para executar aplicações de forma isolada, reproduzível e independente da configuração direta do sistema operacional.

No laboratório, o Docker é utilizado principalmente nos servidores:

```text
APP01
APP02
```

Cada servidor executa a mesma aplicação FastAPI em container.

## Instalação

O Docker Engine foi instalado no Debian 13 utilizando o repositório oficial da Docker.

Pacotes instalados:

```text
docker-ce
docker-ce-cli
containerd.io
docker-buildx-plugin
docker-compose-plugin
```

A instalação pelo repositório oficial é suportada no Debian 13.

## Validação do serviço

O serviço foi validado com:

```bash
sudo systemctl status docker
```

As versões podem ser verificadas com:

```bash
docker --version
docker compose version
```

## Uso de sudo

Os comandos Docker continuam sendo executados com:

```bash
sudo docker
```

O usuário não foi adicionado ao grupo `docker`.

Isso foi mantido propositalmente porque membros do grupo `docker` possuem privilégios equivalentes a root no host.

## Primeiro container

O primeiro teste foi realizado com a imagem oficial:

```bash
sudo docker run hello-world
```

O fluxo observado foi:

```text
Docker CLI
    |
    v
Docker daemon
    |
    +-- procura a imagem localmente
    |
    +-- baixa do registry se necessário
    |
    +-- cria o container
    |
    +-- executa o processo
    |
    +-- encerra o container
```

Esse teste confirmou que:

- o Docker Engine estava funcionando;
- o daemon estava ativo;
- o host conseguia acessar o registry;
- imagens podiam ser baixadas;
- containers podiam ser criados e executados.

## Imagem x Container

### Imagem

Uma imagem é um modelo utilizado para criar containers.

Exemplo:

```text
linux-infra-app:1.1
```

### Container

Um container é uma instância executável criada a partir de uma imagem.

Exemplo:

```text
app01-api
```

Comandos utilizados:

```bash
sudo docker images
sudo docker ps
sudo docker ps -a
```

`docker ps` mostra containers em execução.

`docker ps -a` também mostra containers parados ou finalizados.

## Primeiro teste com Nginx

Antes da aplicação própria, foi criado um container Nginx:

```bash
sudo docker run -d \
  --name nginx-lab \
  -p 10.10.10.21:8080:80 \
  nginx:alpine
```

A publicação da porta funcionava assim:

```text
APP01
10.10.10.21:8080
        |
        v
Docker
        |
        v
nginx-lab:80
```

O acesso foi validado com:

```bash
curl http://10.10.10.21:8080
```

Esse container foi utilizado apenas durante os testes iniciais do Docker.

Posteriormente, o laboratório passou a utilizar uma aplicação FastAPI própria.

## Redes padrão do Docker

As redes iniciais foram verificadas com:

```bash
sudo docker network ls
```

Redes padrão:

```text
bridge
host
none
```

O primeiro container `nginx-lab` recebeu inicialmente um endereço na rede `bridge`.

Exemplo observado:

```text
172.17.0.2
```

## Rede Docker customizada

Foi criada:

```text
app-network
```

Com:

```bash
sudo docker network create app-network
```

Essa rede foi utilizada inicialmente pelo `nginx-lab` e posteriormente pelos containers da aplicação.

Exemplo:

```text
APP01
10.10.10.21
    |
    v
Docker
    |
    v
app-network
    |
    v
app01-api
```

No APP02:

```text
APP02
10.10.10.22
    |
    v
Docker
    |
    v
app-network
    |
    v
app02-api
```

As redes Docker existentes em APP01 e APP02 são locais a cada host.

Apesar de possuírem o mesmo nome:

```text
app-network
```

elas não formam uma única rede distribuída entre as duas VMs.

## DNS interno do Docker

Containers conectados à mesma rede bridge customizada conseguem utilizar resolução de nomes fornecida pelo Docker.

Isso foi testado durante os primeiros experimentos usando um container temporário:

```bash
sudo docker run --rm \
  --network app-network \
  curlimages/curl \
  http://nginx-lab
```

Fluxo:

```text
container temporário
        |
        | nginx-lab
        v
DNS interno Docker
        |
        v
nginx-lab
```

O acesso funcionou sem utilizar diretamente o endereço IP interno do container.

## Containers temporários

A opção:

```text
--rm
```

faz com que o container seja removido automaticamente quando termina sua execução.

Exemplo:

```bash
sudo docker run --rm \
  --network app-network \
  curlimages/curl \
  http://nginx-lab
```

Depois:

```bash
sudo docker ps -a
```

o container temporário não permaneceu listado.

## Aplicação própria

Depois dos testes iniciais com Nginx, foi criada uma aplicação própria utilizando FastAPI.

Estrutura:

```text
app/
├── app.py
├── Dockerfile
├── requirements.txt
├── .dockerignore
└── .env
```

O arquivo `.env` existe somente nos servidores de aplicação e não é versionado.

## Dockerfile

O Dockerfile utilizado atualmente é:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Fluxo de construção:

```text
Dockerfile
    |
    v
python:3.13-slim
    |
    +-- WORKDIR /app
    |
    +-- requirements.txt
    |
    +-- pip install
    |
    +-- app.py
    |
    v
Imagem Docker
```

## Dependências Python

O `requirements.txt` atual contém:

```text
fastapi
uvicorn
psycopg[binary]
```

Função de cada componente:

```text
FastAPI
    -> aplicação/API

Uvicorn
    -> servidor ASGI

Psycopg
    -> comunicação Python/PostgreSQL
```

## Primeira imagem da aplicação

A primeira versão foi criada com:

```bash
sudo docker build -t linux-infra-app:1.0 .
```

Imagem:

```text
linux-infra-app:1.0
```

Essa versão executava a aplicação FastAPI sem integração com PostgreSQL.

## Versão 1.1

Após adicionar Psycopg e o endpoint de health check do banco, foi criada:

```bash
sudo docker build -t linux-infra-app:1.1 .
```

Imagem atual:

```text
linux-infra-app:1.1
```

A imagem contém:

```text
Python 3.13
FastAPI
Uvicorn
Psycopg 3
app.py
```

## .dockerignore

O `.dockerignore` atual contém:

```text
.venv
__pycache__
*.pyc
.git
.gitignore
.env
.env.*
```

Isso evita que arquivos desnecessários ou sensíveis façam parte do contexto de build.

Em especial:

```text
.env
.env.*
```

impedem que arquivos locais contendo credenciais sejam enviados ao contexto de construção.

## Variáveis de ambiente

As configurações de acesso ao PostgreSQL não ficam gravadas na imagem.

Elas são fornecidas ao container através de um arquivo:

```text
.env
```

Estrutura utilizada:

```text
DB_HOST=10.10.10.30
DB_PORT=5432
DB_NAME=linuxinfra
DB_USER=linuxinfra_app
DB_PASSWORD=<senha>
```

O arquivo foi protegido com:

```bash
chmod 600 .env
```

e está ignorado pelo Git.

## Execução no APP01

O container atual é iniciado com:

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

Arquitetura:

```text
APP01
10.10.10.21:8000
        |
        v
Docker
        |
        v
app01-api
FastAPI
```

## Execução no APP02

O APP02 executa a mesma imagem:

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

Arquitetura:

```text
APP02
10.10.10.22:8000
        |
        v
Docker
        |
        v
app02-api
FastAPI
```

## Hostname dos containers

Os containers foram configurados explicitamente com:

```text
--hostname app01
```

e:

```text
--hostname app02
```

Isso permite que a aplicação identifique qual instância respondeu à requisição.

Exemplo:

```json
{
  "app": "linux-infra-lab",
  "hostname": "app01",
  "status": "ok"
}
```

ou:

```json
{
  "app": "linux-infra-lab",
  "hostname": "app02",
  "status": "ok"
}
```

Esse comportamento também foi utilizado para validar o load balancing.

## Publicação de portas

APP01:

```text
10.10.10.21:8000
        |
        v
container:8000
```

APP02:

```text
10.10.10.22:8000
        |
        v
container:8000
```

O PROXY01 acessa esses endereços diretamente.

## Restart policy

Os containers utilizam:

```text
--restart unless-stopped
```

Isso permite que sejam reiniciados automaticamente quando o Docker daemon reinicia, exceto quando tiverem sido parados explicitamente.

## Integração com PostgreSQL

A aplicação utiliza Psycopg dentro do container.

Fluxo:

```text
app01-api
FastAPI
   |
   v
Psycopg
   |
   v
10.10.10.30:5432
DB01
PostgreSQL
```

O mesmo acontece no APP02.

As configurações são obtidas das variáveis:

```text
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
```

## Health check do banco

A aplicação possui:

```text
GET /health/db
```

No APP01:

```bash
curl http://10.10.10.21:8000/health/db
```

Resposta validada:

```json
{
  "status": "healthy",
  "database": "connected",
  "hostname": "app01"
}
```

No APP02:

```bash
curl http://10.10.10.22:8000/health/db
```

Resposta validada:

```json
{
  "status": "healthy",
  "database": "connected",
  "hostname": "app02"
}
```

Isso valida:

```text
Container
   |
FastAPI
   |
Psycopg
   |
PostgreSQL
```

## Docker e rede Hyper-V

A rede Docker e a rede Hyper-V possuem funções diferentes.

Rede Hyper-V:

```text
10.10.10.0/24
```

é utilizada para comunicação entre as VMs.

Já `app-network` é uma rede interna do Docker em cada servidor.

Exemplo:

```text
PROXY01
10.10.10.10
      |
      v
APP01
10.10.10.21
      |
      v
porta publicada 8000
      |
      v
app01-api
app-network
```

## Estado atual

APP01:

```text
linux-infra-app:1.1
        |
        v
app01-api
```

APP02:

```text
linux-infra-app:1.1
        |
        v
app02-api
```

Os dois containers:

- executam FastAPI;
- utilizam Psycopg;
- acessam o mesmo PostgreSQL;
- possuem restart policy;
- recebem configuração por variáveis de ambiente;
- participam do balanceamento realizado pelo PROXY01.

## Evolução do uso de Docker

O laboratório evoluiu da seguinte forma:

```text
hello-world
     |
     v
Nginx container
     |
     v
rede app-network
     |
     v
FastAPI local
     |
     v
Dockerfile
     |
     v
linux-infra-app:1.0
     |
     v
APP01 + APP02
     |
     v
Psycopg
     |
     v
linux-infra-app:1.1
     |
     v
PostgreSQL
```

## Próximos passos

As próximas evoluções relacionadas a Docker incluem:

- adicionar endpoints reais de leitura e escrita;
- evoluir a aplicação para novas versões;
- utilizar connection pooling;
- avaliar Docker Compose;
- automatizar o build das imagens;
- automatizar deploy;
- criar pipeline CI/CD;
- adicionar métricas dos containers;
- monitorar consumo de CPU e memória;
- estudar persistência com volumes;
- implementar testes de atualização e rollback.