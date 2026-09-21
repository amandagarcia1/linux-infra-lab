# Arquitetura

Este documento descreve a arquitetura atual do laboratório `linux-infra-lab` e sua evolução planejada.

## Objetivo da arquitetura

O objetivo é construir uma infraestrutura Linux dividindo as principais funções em máquinas virtuais independentes.

Cada servidor possui uma responsabilidade específica:

- `PROXY01`: entrada das requisições, reverse proxy e balanceamento de carga.
- `APP01`: primeira instância da aplicação FastAPI.
- `APP02`: segunda instância da aplicação FastAPI.
- `DB01`: servidor PostgreSQL compartilhado pelas aplicações.

Essa separação permite estudar individualmente:

- redes;
- Linux;
- containers;
- reverse proxy;
- balanceamento de carga;
- failover;
- banco de dados;
- comunicação entre aplicações;
- segurança;
- observabilidade;
- alta disponibilidade.

## Arquitetura atual

O laboratório é executado em um host Windows com Hyper-V.

As máquinas virtuais utilizam a rede interna:

```text
LAB-INFRA
10.10.10.0/24
```

O host Windows possui:

```text
10.10.10.1
```

e realiza NAT para permitir que as VMs tenham acesso externo.

A arquitetura atual é:

```text
                         Windows Host
                              |
                           Hyper-V
                              |
                         LAB-INFRA
                        10.10.10.0/24
                              |
        +---------------------+---------------------+
        |                     |                     |
        |                     |                     |
     PROXY01                APP01                 APP02
   10.10.10.10            10.10.10.21           10.10.10.22
      Nginx                 Docker                 Docker
        |                   FastAPI                FastAPI
        |                   Psycopg                Psycopg
        |                     |                      |
        +----------+----------+----------+-----------+
                   |                     |
                   +----------+----------+
                              |
                              v
                            DB01
                        10.10.10.30
                        PostgreSQL 17
```

## Fluxo da aplicação

O cliente não acessa diretamente os servidores de aplicação.

As requisições entram pelo `PROXY01`:

```text
Cliente
   |
   v
PROXY01
10.10.10.10
Nginx
   |
   +----------> APP01
   |          10.10.10.21
   |
   +----------> APP02
              10.10.10.22
```

O Nginx distribui as requisições entre os dois servidores de aplicação.

APP01 e APP02 executam a mesma aplicação FastAPI em containers Docker.

Cada instância da aplicação utiliza o Psycopg para se comunicar com o PostgreSQL:

```text
APP01 --------\
               \
                ---> DB01
               /     PostgreSQL
APP02 --------/
```

Isso permite que ambas as instâncias da aplicação utilizem o mesmo estado persistente.

## PROXY01

Servidor responsável pela entrada das requisições.

### Identificação

```text
Hostname: proxy01
IP: 10.10.10.10
Sistema operacional: Debian 13
```

### Tecnologias

- Debian 13
- Nginx
- reverse proxy
- load balancing

### Função

O Nginx recebe as requisições HTTP e distribui entre:

```text
APP01 - 10.10.10.21:8000
APP02 - 10.10.10.22:8000
```

O algoritmo utilizado atualmente é o round-robin padrão do Nginx.

Também foi configurada detecção passiva de falhas dos backends.

## APP01

Primeiro servidor de aplicação.

### Identificação

```text
Hostname: app01
IP: 10.10.10.21
Sistema operacional: Debian 13
```

### Tecnologias

- Debian 13
- Docker Engine
- FastAPI
- Psycopg 3
- PostgreSQL Client

### Aplicação

A aplicação roda em container Docker:

```text
app01-api
```

Imagem atual:

```text
linux-infra-app:1.1
```

Porta publicada:

```text
10.10.10.21:8000
```

O container utiliza variáveis de ambiente para receber as configurações de conexão com o PostgreSQL.

## APP02

Segundo servidor de aplicação.

### Identificação

```text
Hostname: app02
IP: 10.10.10.22
Sistema operacional: Debian 13
```

### Tecnologias

- Debian 13
- Docker Engine
- FastAPI
- Psycopg 3
- PostgreSQL Client

### Aplicação

A aplicação roda em container Docker:

```text
app02-api
```

Imagem atual:

```text
linux-infra-app:1.1
```

Porta publicada:

```text
10.10.10.22:8000
```

APP01 e APP02 executam a mesma aplicação e acessam o mesmo banco PostgreSQL.

## DB01

Servidor dedicado ao banco de dados.

### Identificação

```text
Hostname: db01
IP: 10.10.10.30
Sistema operacional: Debian 13
```

### Tecnologia

```text
PostgreSQL 17
```

Banco utilizado pela aplicação:

```text
linuxinfra
```

Role utilizada:

```text
linuxinfra_app
```

O PostgreSQL está configurado para escutar em:

```text
10.10.10.30:5432
```

O acesso remoto foi restringido aos servidores:

```text
APP01 - 10.10.10.21
APP02 - 10.10.10.22
```

## Comunicação FastAPI com PostgreSQL

A aplicação não se conecta ao PostgreSQL diretamente através de comandos manuais.

O fluxo utilizado é:

```text
FastAPI
   |
   v
Psycopg
   |
   v
PostgreSQL
```

O Psycopg funciona como driver PostgreSQL para Python.

As informações de conexão são fornecidas ao container através de variáveis de ambiente:

```text
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
```

A senha não é armazenada no código-fonte nem versionada no Git.

## Health checks

A aplicação possui:

```text
GET /
```

para verificar a aplicação.

Também possui:

```text
GET /health
```

para verificar o estado da instância.

E:

```text
GET /health/db
```

para validar a comunicação:

```text
FastAPI
   |
Psycopg
   |
PostgreSQL
```

O endpoint foi validado com sucesso em APP01 e APP02.

## Balanceamento de carga

O `PROXY01` utiliza Nginx para distribuir as requisições entre:

```text
APP01
APP02
```

Fluxo normal:

```text
             PROXY01
                |
        +-------+-------+
        |               |
        v               v
      APP01           APP02
```

As requisições são distribuídas entre os dois nós.

## Failover da aplicação

O comportamento de falha de um servidor de aplicação já foi testado.

Exemplo com APP01 indisponível:

```text
             PROXY01
                |
        +-------+-------+
        |               |
        v               v
      APP01           APP02
        X               |
                        |
                        v
                       OK
```

Durante a indisponibilidade do APP01, o serviço continuou sendo atendido pelo APP02.

Após o retorno do APP01, o balanceamento voltou a utilizar os dois servidores.

## Persistência compartilhada

APP01 e APP02 foram testados acessando o mesmo banco PostgreSQL.

Um registro criado a partir do APP01:

```text
origem: app01
```

foi visualizado pelo APP02.

Também foi criado um registro pelo APP02:

```text
origem: app02
```

e ambos permaneceram disponíveis no mesmo banco.

Isso valida o modelo:

```text
APP01 ----\
           \
            ---> PostgreSQL
           /
APP02 ----/
```

## Pontos únicos de falha atuais

Apesar da redundância da camada de aplicação, ainda existem pontos únicos de falha.

### PROXY01

Atualmente existe apenas um servidor Nginx.

Se o `PROXY01` ficar indisponível:

```text
Cliente
   |
   X
PROXY01
```

APP01 e APP02 podem continuar funcionando, mas deixam de ser acessíveis através do endereço principal da aplicação.

### DB01

Existe atualmente apenas um servidor PostgreSQL.

Se o `DB01` ficar indisponível:

```text
APP01 ----X
           \
            DB01 indisponível
           /
APP02 ----X
```

as duas aplicações perdem acesso ao banco.

Esses pontos serão tratados em etapas futuras.

## Evolução prevista

A arquitetura será expandida gradualmente.

### Banco de dados

- criar `DB02`;
- configurar replicação PostgreSQL;
- testar failover;
- implementar backup;
- testar restauração;
- avaliar Patroni;
- estudar alta disponibilidade do PostgreSQL.

### Proxy

- criar `PROXY02`;
- configurar redundância;
- implementar IP virtual;
- estudar Keepalived/VRRP;
- testar failover do proxy.

### Aplicação

- implementar endpoints de leitura e escrita;
- validar persistência através do balanceador;
- evoluir gerenciamento de conexões com PostgreSQL;
- avaliar connection pool;
- avaliar SQLAlchemy e migrations.

### Observabilidade

- Prometheus;
- Grafana;
- métricas da aplicação;
- métricas do Nginx;
- métricas do PostgreSQL;
- centralização de logs;
- alertas.

### Automação

- Docker Compose;
- Ansible;
- automação de configuração;
- CI/CD;
- deploy automatizado.

### Resiliência

- testes controlados de falha;
- recuperação de serviços;
- testes de indisponibilidade de APPs;
- testes de indisponibilidade de proxy;
- testes de indisponibilidade de banco;
- documentação dos procedimentos de recuperação.

## Objetivo final

O objetivo não é apenas criar uma infraestrutura funcional.

O laboratório busca permitir o entendimento prático de como cada camada funciona e como elas se relacionam:

```text
Rede
  |
Linux
  |
Containers
  |
Aplicação
  |
Load Balancer
  |
Banco de Dados
  |
Alta Disponibilidade
  |
Observabilidade
  |
Automação
```

Cada nova camada será adicionada após a validação da anterior, permitindo entender os problemas que cada tecnologia resolve antes de adicionar novas abstrações.