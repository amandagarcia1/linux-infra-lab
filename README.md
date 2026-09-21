# Linux Infra Lab

Laboratório prático de infraestrutura Linux com foco em aprimoramento de:

- Linux
- Hyper-V
- redes
- SSH
- Docker
- Nginx
- PostgreSQL
- FastAPI
- Psycopg
- load balancing
- failover
- observabilidade
- segurança
- automação

## Arquitetura atual

O laboratório roda em Hyper-V usando uma rede interna isolada.

```text
Windows Host
    |
    | NAT
    |
LAB-INFRA - 10.10.10.0/24
    |
    +-- PROXY01 - 10.10.10.10
    |      |
    |      +-- Nginx
    |      +-- Load Balancer
    |
    +-- APP01 - 10.10.10.21
    |      |
    |      +-- Docker
    |      +-- FastAPI
    |      +-- Psycopg
    |
    +-- APP02 - 10.10.10.22
    |      |
    |      +-- Docker
    |      +-- FastAPI
    |      +-- Psycopg
    |
    +-- DB01 - 10.10.10.30
           |
           +-- PostgreSQL 17
```

## Fluxo atual da aplicação

```text
Cliente
   |
   v
PROXY01
Nginx
   |
   +------> APP01
   |         |
   |         v
   |       FastAPI
   |         |
   |         v
   |       Psycopg
   |         |
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

APP01 e APP02 utilizam o mesmo banco PostgreSQL, permitindo que ambas as instâncias compartilhem o mesmo estado persistente.

## Status

### Infraestrutura base

- [x] Criar rede LAB-INFRA no Hyper-V
- [x] Configurar NAT
- [x] Criar APP01
- [x] Instalar Debian 13
- [x] Configurar SSH
- [x] Configurar autenticação SSH por chave
- [x] Instalar Docker Engine
- [x] Criar rede Docker customizada
- [x] Executar Nginx em container para testes iniciais

### Aplicação

- [x] Criar aplicação própria com FastAPI
- [x] Criar Dockerfile
- [x] Criar imagem Docker da aplicação
- [x] Executar aplicação em container no APP01
- [x] Criar APP02
- [x] Executar aplicação em container no APP02
- [x] Configurar restart policy dos containers

### Proxy e balanceamento

- [x] Criar PROXY01
- [x] Instalar Nginx no PROXY01
- [x] Configurar reverse proxy
- [x] Configurar load balancing entre APP01 e APP02
- [x] Configurar detecção passiva de falhas
- [x] Testar distribuição de requisições
- [x] Testar failover da aplicação
- [x] Validar retorno do backend após recuperação

### Banco de dados

- [x] Criar DB01
- [x] Instalar PostgreSQL 17
- [x] Criar banco `linuxinfra`
- [x] Criar usuário `linuxinfra_app`
- [x] Configurar acesso remoto ao PostgreSQL
- [x] Configurar `listen_addresses`
- [x] Restringir acesso ao APP01 e APP02 via `pg_hba.conf`
- [x] Configurar autenticação SCRAM-SHA-256
- [x] Validar conexão do APP01 com o PostgreSQL
- [x] Validar conexão do APP02 com o PostgreSQL
- [x] Criar tabela de teste
- [x] Validar leitura e escrita compartilhada entre APP01 e APP02

### Integração FastAPI + PostgreSQL

- [x] Adicionar Psycopg 3 à aplicação
- [x] Configurar conexão por variáveis de ambiente
- [x] Criar arquivo `.env` local nos servidores de aplicação
- [x] Proteger o `.env`
- [x] Adicionar `.env` ao `.dockerignore`
- [x] Criar endpoint `/health/db`
- [x] Validar FastAPI → Psycopg → PostgreSQL no APP01
- [x] Validar FastAPI → Psycopg → PostgreSQL no APP02
- [x] Criar imagem `linux-infra-app:1.1`
- [x] Atualizar APP01 e APP02 para a versão 1.1

### Documentação

- [x] Atualizar arquitetura do laboratório
- [x] Atualizar documentação da rede Hyper-V
- [x] Atualizar documentação do APP01
- [x] Atualizar documentação de Docker
- [x] Atualizar documentação de Nginx, load balancing e failover
- [x] Documentar PostgreSQL
- [x] Documentar integração FastAPI + PostgreSQL

### Próximos passos

- [ ] Criar endpoint `GET /records`
- [ ] Criar endpoint `POST /records`
- [ ] Testar leitura pelo PROXY01
- [ ] Testar escrita pelo PROXY01
- [ ] Validar persistência compartilhada através do balanceador
- [ ] Melhorar tratamento de erros da aplicação
- [ ] Avaliar connection pooling
- [ ] Implementar backup do PostgreSQL
- [ ] Testar restauração do banco
- [ ] Criar DB02
- [ ] Configurar replicação PostgreSQL
- [ ] Estudar failover do banco
- [ ] Avaliar Patroni
- [ ] Criar PROXY02
- [ ] Implementar HA do proxy
- [ ] Avaliar Keepalived/VRRP
- [ ] Implementar observabilidade
- [ ] Implementar métricas
- [ ] Implementar centralização de logs
- [ ] Implementar alertas
- [ ] Avaliar Docker Compose
- [ ] Implementar Ansible
- [ ] Implementar CI/CD
- [ ] Automatizar build e deploy
- [ ] Implementar testes controlados de falha

## Documentação

- [Arquitetura](docs/01-architecture.md)
- [Rede Hyper-V](docs/02-hyperv-network.md)
- [APP01 - Debian](docs/03-app01-debian.md)
- [Docker](docs/04-docker-basics.md)
- [Nginx - Load Balancing e Failover](docs/05-nginx-load-balancing.md)
- [PostgreSQL](docs/06-postgresql.md)
- [FastAPI + PostgreSQL](docs/07-fastapi-postgresql.md)

## Tecnologias utilizadas

```text
Windows
Hyper-V
Debian 13
SSH
Docker Engine
FastAPI
Uvicorn
Psycopg 3
Nginx
PostgreSQL 17
Git
GitHub
```

## Serviços atuais

| Servidor | IP | Função |
|---|---|---|
| PROXY01 | `10.10.10.10` | Nginx / Reverse Proxy / Load Balancer |
| APP01 | `10.10.10.21` | Docker / FastAPI / Psycopg |
| APP02 | `10.10.10.22` | Docker / FastAPI / Psycopg |
| DB01 | `10.10.10.30` | PostgreSQL 17 |

## Estado atual da arquitetura

```text
                    Cliente
                       |
                       v
                    PROXY01
                     Nginx
                       |
             +---------+---------+
             |                   |
             v                   v
           APP01               APP02
           Docker              Docker
           FastAPI             FastAPI
           Psycopg             Psycopg
             \                   /
              \                 /
               +---------------+
                       |
                       v
                      DB01
                  PostgreSQL 17
```

A camada de aplicação possui redundância entre APP01 e APP02.

Atualmente ainda existem dois principais pontos únicos de falha:

```text
PROXY01
DB01
```

Esses componentes serão tratados nas próximas etapas do laboratório com redundância e alta disponibilidade.

## Objetivo

O objetivo deste projeto é construir uma infraestrutura Linux do zero e entender cada componente antes de adicionar camadas de abstração e automação.

O laboratório é evoluído gradualmente, começando por:

```text
rede
  |
  v
Linux
  |
  v
SSH
  |
  v
Docker
  |
  v
aplicação
  |
  v
load balancing
  |
  v
PostgreSQL
  |
  v
alta disponibilidade
  |
  v
observabilidade
  |
  v
automação
```

A proposta é entender primeiro o funcionamento de cada camada e os problemas que ela resolve antes de adicionar ferramentas mais avançadas.