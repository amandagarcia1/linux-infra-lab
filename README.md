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

Fluxo atual da aplicação

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

Status

Infraestrutura base

 Criar rede LAB-INFRA no Hyper-V
 Configurar NAT
 Criar APP01
 Instalar Debian 13
 Configurar SSH
 Configurar autenticação SSH por chave
 Instalar Docker Engine
 Criar rede Docker customizada
 Executar Nginx em container

Aplicação

 Criar aplicação própria com FastAPI
 Criar Dockerfile
 Criar imagem Docker da aplicação
 Executar aplicação em container no APP01
 Criar APP02
 Executar aplicação em container no APP02

Proxy e balanceamento

 Criar PROXY01
 Instalar Nginx no PROXY01
 Configurar reverse proxy
 Configurar load balancing entre APP01 e APP02
 Testar distribuição de requisições
 Testar failover da aplicação

Banco de dados

 Criar DB01
 Instalar PostgreSQL 17
 Criar banco linuxinfra
 Criar usuário linuxinfra_app
 Configurar acesso remoto ao PostgreSQL
 Restringir acesso ao APP01 e APP02
 Validar conexão do APP01 com o PostgreSQL
 Validar conexão do APP02 com o PostgreSQL
 Validar leitura e escrita compartilhada entre APP01 e APP02

Integração FastAPI + PostgreSQL

 Adicionar Psycopg 3 à aplicação
 Configurar conexão por variáveis de ambiente
 Criar endpoint /health/db
 Validar FastAPI → Psycopg → PostgreSQL no APP01
 Validar FastAPI → Psycopg → PostgreSQL no APP02
 Criar imagem linux-infra-app:1.1
 Atualizar APP01 e APP02 para a versão 1.1

Próximos passos

 Criar endpoint GET /records
 Criar endpoint POST /records
 Testar leitura pelo PROXY01
 Testar escrita pelo PROXY01
 Validar persistência compartilhada através do balanceador
 Documentar integração FastAPI + PostgreSQL
 Implementar backup do PostgreSQL
 Testar restauração do banco
 Criar DB02
 Configurar replicação PostgreSQL
 Estudar failover do banco
 Avaliar Patroni
 Criar PROXY02
 Implementar HA do proxy
 Implementar observabilidade
 Implementar automação

Documentação

Arquitetura inicial
Rede Hyper-V
APP01 - Debian
Docker básico
Nginx - Load Balancing e Failover

Objetivo

O objetivo deste projeto é construir uma infraestrutura Linux do zero e entender cada componente antes de adicionar camadas de automação.

O laboratório é evoluído gradualmente, começando por rede, Linux, Docker e aplicação, avançando depois para balanceamento de carga, persistência em banco de dados, alta disponibilidade, observabilidade, segurança, automação e testes de falha.

A proposta é entender primeiro o funcionamento de cada camada antes de abstraí-la com ferramentas mais avançadas.