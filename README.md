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
   |       Psycopg
   |         |
   +------> APP02
             |
             v
           Psycopg
             |
             v
            DB01
         PostgreSQL
```

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
- [x] Executar Nginx em container

### Aplicação

- [x] Criar aplicação própria com FastAPI
- [x] Criar Dockerfile
- [x] Criar imagem Docker da aplicação
- [x] Executar aplicação em container no APP01
- [x] Criar APP02
- [x] Executar aplicação em container no APP02

### Proxy e balanceamento

- [x] Criar PROXY01
- [x] Instalar Nginx no PROXY01
- [x] Configurar reverse proxy
- [x] Configurar load balancing entre APP01 e APP02
- [x] Testar distribuição de requisições
- [x] Testar failover da aplicação

### Banco de dados

- [x] Criar DB01
- [x] Instalar PostgreSQL 17
- [x] Criar banco `linuxinfra`
- [x] Criar usuário `linuxinfra_app`
- [x] Configurar acesso remoto ao PostgreSQL
- [x] Restringir acesso ao APP01 e APP02
- [x] Validar conexão do APP01 com o PostgreSQL
- [x] Validar conexão do APP02 com o PostgreSQL
- [x] Validar leitura e escrita compartilhada entre APP01 e APP02

### Integração FastAPI + PostgreSQL

- [x] Adicionar Psycopg 3 à aplicação
- [x] Configurar conexão por variáveis de ambiente
- [x] Criar endpoint `/health/db`
- [x] Validar FastAPI → Psycopg → PostgreSQL no APP01
- [x] Validar FastAPI → Psycopg → PostgreSQL no APP02
- [x] Criar imagem `linux-infra-app:1.1`
- [x] Atualizar APP01 e APP02 para a versão 1.1

### Próximos passos

- [ ] Criar endpoint `GET /records`
- [ ] Criar endpoint `POST /records`
- [ ] Testar leitura pelo PROXY01
- [ ] Testar escrita pelo PROXY01
- [ ] Validar persistência compartilhada através do balanceador
- [ ] Documentar integração FastAPI + PostgreSQL
- [ ] Implementar backup do PostgreSQL
- [ ] Testar restauração do banco
- [ ] Criar DB02
- [ ] Configurar replicação PostgreSQL
- [ ] Estudar failover do banco
- [ ] Avaliar Patroni
- [ ] Criar PROXY02
- [ ] Implementar HA do proxy
- [ ] Implementar observabilidade
- [ ] Implementar automação

## Documentação

- [Arquitetura inicial](docs/01-architecture.md)
- [Rede Hyper-V](docs/02-hyperv-network.md)
- [APP01 - Debian](docs/03-app01-debian.md)
- [Docker básico](docs/04-docker-basics.md)
- [Nginx - Load Balancing e Failover](docs/05-nginx-load-balancing.md)

## Objetivo

O objetivo deste projeto é construir uma infraestrutura Linux do zero e entender cada componente antes de adicionar camadas de automação.

O laboratório é evoluído gradualmente, começando por rede, Linux, Docker e aplicação, avançando depois para balanceamento de carga, persistência em banco de dados, alta disponibilidade, observabilidade, segurança, automação e testes de falha.

A proposta é entender primeiro o funcionamento de cada camada antes de abstraí-la com ferramentas mais avançadas.