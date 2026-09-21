# PostgreSQL

Este documento descreve a instalação, configuração e validação do PostgreSQL no servidor `DB01`.

## Objetivo

Centralizar os dados da aplicação em um banco PostgreSQL compartilhado por `APP01` e `APP02`.

Arquitetura:

```text
APP01
10.10.10.21
     \
      \
       ---> DB01
            10.10.10.30
            PostgreSQL 17
      /
     /
APP02
10.10.10.22
```

O objetivo é garantir que as duas instâncias da aplicação utilizem o mesmo estado persistente.

## DB01

Identificação:

```text
Hostname: db01
FQDN: db01.lab.home.arpa
IP: 10.10.10.30/24
Gateway: 10.10.10.1
Sistema operacional: Debian 13
```

Recursos iniciais:

```text
vCPU: 2
RAM: 2 GB
Disco: 20 GB
```

## Instalação

O PostgreSQL foi instalado utilizando os pacotes disponibilizados pelo Debian 13.

```bash
sudo apt update
sudo apt install -y postgresql
```

A versão instalada foi:

```text
PostgreSQL 17.11
```

Validação:

```bash
psql --version
```

Resultado observado:

```text
psql (PostgreSQL) 17.11
```

## Cluster PostgreSQL

Os clusters existentes foram verificados com:

```bash
sudo pg_lsclusters
```

Resultado:

```text
Ver Cluster Port Status Owner
17  main    5432 online postgres
```

Diretório de dados:

```text
/var/lib/postgresql/17/main
```

Arquivo de log:

```text
/var/log/postgresql/postgresql-17-main.log
```

## Serviço PostgreSQL

Validação:

```bash
sudo systemctl status postgresql --no-pager
```

O serviço agregador `postgresql.service` pode aparecer como:

```text
active (exited)
```

enquanto o cluster PostgreSQL permanece ativo.

O estado efetivo do cluster foi confirmado com:

```bash
sudo pg_lsclusters
```

Resultado:

```text
17 main 5432 online
```

## Primeiro acesso

O acesso administrativo local foi realizado usando a role `postgres`:

```bash
sudo -u postgres psql
```

Dentro do PostgreSQL:

```sql
SELECT version();
```

Também foram utilizados:

```text
\l
```

para listar bancos e:

```text
\du
```

para listar roles.

## Bancos iniciais

Após a instalação existiam:

```text
postgres
template0
template1
```

Esses bancos são criados durante a inicialização do cluster PostgreSQL.

## Role da aplicação

Foi criada uma role específica para a aplicação:

```text
linuxinfra_app
```

A role possui capacidade de login, mas não possui privilégios administrativos.

Criação:

```sql
CREATE ROLE linuxinfra_app
WITH
    LOGIN
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    NOREPLICATION
    PASSWORD '<senha>';
```

A aplicação não utiliza a role administrativa `postgres`.

Isso reduz o nível de privilégio disponível para a aplicação.

No PostgreSQL, roles com `LOGIN` podem ser utilizadas para autenticação, enquanto uma role `SUPERUSER` pode ignorar praticamente todas as verificações de permissão. Por isso foi utilizada uma role comum para a aplicação. :contentReference[oaicite:0]{index=0}

## Banco da aplicação

Foi criado:

```text
linuxinfra
```

Owner:

```text
linuxinfra_app
```

Comando:

```sql
CREATE DATABASE linuxinfra
OWNER linuxinfra_app;
```

O proprietário de um banco possui controle sobre aquele banco, sem necessidade de tornar a role superusuária. :contentReference[oaicite:1]{index=1}

## Validação

Dentro do `psql`:

```text
\du
```

Resultado esperado:

```text
linuxinfra_app
postgres
```

A role `linuxinfra_app` aparece sem privilégios administrativos adicionais.

Também:

```text
\l
```

mostra:

```text
linuxinfra | linuxinfra_app
```

## Arquivos de configuração

Os arquivos efetivamente utilizados pelo PostgreSQL foram confirmados com:

```bash
sudo -u postgres psql -c "SHOW config_file;"
```

Resultado:

```text
/etc/postgresql/17/main/postgresql.conf
```

E:

```bash
sudo -u postgres psql -c "SHOW hba_file;"
```

Resultado:

```text
/etc/postgresql/17/main/pg_hba.conf
```

## Escuta de rede

Por padrão, o PostgreSQL estava escutando apenas localmente.

Validação inicial:

```bash
sudo -u postgres psql -c "SHOW listen_addresses;"
```

Resultado inicial:

```text
localhost
```

Também:

```bash
sudo ss -lntp | grep 5432
```

mostrava:

```text
127.0.0.1:5432
[::1]:5432
```

Isso impedia conexões remotas.

## Configuração de listen_addresses

Foi alterado:

```text
/etc/postgresql/17/main/postgresql.conf
```

A configuração passou a utilizar:

```text
listen_addresses = '10.10.10.30'
```

Isso faz com que o PostgreSQL escute especificamente no endereço interno do DB01.

O PostgreSQL permite controlar em quais interfaces TCP/IP o servidor aceita conexões através de `listen_addresses`. :contentReference[oaicite:2]{index=2}

Depois da alteração:

```bash
sudo systemctl restart postgresql
```

Validação:

```bash
sudo -u postgres psql -c "SHOW listen_addresses;"
```

Resultado:

```text
10.10.10.30
```

E:

```bash
sudo ss -lntp | grep 5432
```

Resultado:

```text
LISTEN ... 10.10.10.30:5432
```

## Controle de acesso com pg_hba.conf

O arquivo:

```text
/etc/postgresql/17/main/pg_hba.conf
```

define quais clientes podem autenticar no PostgreSQL.

Foram adicionadas:

```text
host    linuxinfra    linuxinfra_app    10.10.10.21/32    scram-sha-256
host    linuxinfra    linuxinfra_app    10.10.10.22/32    scram-sha-256
```

Essas regras permitem somente:

```text
APP01
10.10.10.21
```

e:

```text
APP02
10.10.10.22
```

para acessar:

```text
Banco: linuxinfra
Role: linuxinfra_app
```

utilizando autenticação:

```text
SCRAM-SHA-256
```

O PostgreSQL processa as regras do `pg_hba.conf` para definir quais clientes, bancos, roles e métodos de autenticação são permitidos. O método `scram-sha-256` utiliza autenticação baseada em senha SCRAM-SHA-256. :contentReference[oaicite:3]{index=3}

## Uso de /32

As regras utilizam:

```text
10.10.10.21/32
10.10.10.22/32
```

O `/32` representa um único endereço IPv4.

Isso é mais restritivo do que liberar toda a rede:

```text
10.10.10.0/24
```

Portanto somente os dois servidores de aplicação autorizados podem utilizar essas regras.

## Validação do pg_hba.conf

A configuração foi verificada através da view:

```text
pg_hba_file_rules
```

Com:

```bash
sudo -u postgres psql -c "SELECT line_number, type, database, user_name, address, auth_method, error FROM pg_hba_file_rules WHERE error IS NOT NULL;"
```

O esperado é:

```text
0 linhas
```

As regras específicas foram verificadas com:

```bash
sudo -u postgres psql -c "SELECT line_number, type, database, user_name, address, auth_method FROM pg_hba_file_rules WHERE address IN ('10.10.10.21','10.10.10.22');"
```

Resultado validado:

```text
host | {linuxinfra} | {linuxinfra_app} | 10.10.10.21 | scram-sha-256
host | {linuxinfra} | {linuxinfra_app} | 10.10.10.22 | scram-sha-256
```

## Teste a partir do APP01

Foi instalado o cliente PostgreSQL:

```bash
sudo apt install -y postgresql-client
```

Depois:

```bash
psql -h 10.10.10.30 \
     -U linuxinfra_app \
     -d linuxinfra
```

A conexão foi realizada com sucesso.

Dentro do PostgreSQL:

```sql
SELECT current_database(), current_user;
```

Resultado:

```text
current_database: linuxinfra
current_user: linuxinfra_app
```

## Teste a partir do APP02

O mesmo teste foi realizado a partir do APP02:

```bash
psql -h 10.10.10.30 \
     -U linuxinfra_app \
     -d linuxinfra
```

A conexão também foi concluída com sucesso.

## TLS

Durante os testes com `psql`, a conexão negociou:

```text
TLSv1.3
```

Exemplo observado:

```text
SSL connection
protocol: TLSv1.3
cipher: TLS_AES_256_GCM_SHA384
```

Isso confirmou que a conexão testada utilizou criptografia TLS.

A regra atual no `pg_hba.conf` utiliza:

```text
host
```

e não:

```text
hostssl
```

Portanto a configuração atual não obriga exclusivamente conexões TLS.

Essa política poderá ser endurecida futuramente.

## Tabela de teste

Foi criada a tabela:

```sql
CREATE TABLE lab_test (
    id SERIAL PRIMARY KEY,
    origem VARCHAR(20) NOT NULL,
    mensagem TEXT NOT NULL,
    criado_em TIMESTAMPTZ DEFAULT NOW()
);
```

Ela foi utilizada para validar a persistência compartilhada.

## Escrita pelo APP01

Foi inserido:

```sql
INSERT INTO lab_test (origem, mensagem)
VALUES ('app01', 'Registro criado pelo APP01');
```

Resultado:

```text
id: 1
origem: app01
```

## Escrita pelo APP02

Depois:

```sql
INSERT INTO lab_test (origem, mensagem)
VALUES ('app02', 'Registro criado pelo APP02');
```

Resultado:

```text
id: 2
origem: app02
```

## Leitura compartilhada

Consulta:

```sql
SELECT * FROM lab_test ORDER BY id;
```

Resultado validado:

```text
1 | app01 | Registro criado pelo APP01
2 | app02 | Registro criado pelo APP02
```

Isso confirmou:

```text
APP01 ----\
           \
            ---> mesmo banco PostgreSQL
           /
APP02 ----/
```

## Persistência

Os dados não pertencem aos containers da aplicação.

Eles são armazenados no DB01:

```text
DB01
PostgreSQL
```

Portanto APP01 e APP02 podem ser recriados sem que os registros armazenados no PostgreSQL desapareçam.

## Integração com FastAPI

Depois da validação manual via `psql`, a aplicação FastAPI foi integrada ao PostgreSQL usando Psycopg.

Fluxo:

```text
FastAPI
   |
   v
Psycopg
   |
   v
DB01
10.10.10.30:5432
```

As informações de conexão são fornecidas aos containers através de:

```text
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
```

## Health check do banco

Foi implementado:

```text
GET /health/db
```

No APP01:

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

No APP02:

```bash
curl http://10.10.10.22:8000/health/db
```

Resultado:

```json
{
  "status": "healthy",
  "database": "connected",
  "hostname": "app02"
}
```

Isso validou:

```text
APP01 FastAPI
      |
      v
    Psycopg
      |
      v
 PostgreSQL


APP02 FastAPI
      |
      v
    Psycopg
      |
      v
 PostgreSQL
```

## Segurança atual

Foram aplicadas as seguintes medidas:

- role própria para a aplicação;
- aplicação não utiliza superuser;
- role sem `CREATEDB`;
- role sem `CREATEROLE`;
- role sem privilégios de replicação;
- PostgreSQL escuta somente em `10.10.10.30`;
- acesso permitido apenas para APP01 e APP02;
- autenticação SCRAM-SHA-256;
- credenciais fora do código-fonte;
- arquivo `.env` não versionado no Git.

## Ponto único de falha

Atualmente existe apenas:

```text
DB01
```

Portanto:

```text
APP01 OK
APP02 OK
DB01 X
```

resulta em indisponibilidade das operações dependentes do banco.

O balanceamento entre APP01 e APP02 não elimina esse ponto único de falha.

## Próxima evolução

A sequência planejada para a camada de banco é:

```text
DB01
  |
  v
backup
  |
  v
restore test
  |
  v
DB02
  |
  v
replicação
  |
  v
failover
  |
  v
HA
```

## Evoluções futuras

Estão previstas:

- backup do PostgreSQL;
- teste de restauração;
- criação do `DB02`;
- replicação PostgreSQL;
- estudo de primary/standby;
- failover;
- avaliação do Patroni;
- connection pooling;
- observabilidade do banco;
- métricas PostgreSQL;
- alertas;
- testes de indisponibilidade;
- políticas mais rígidas de TLS;
- revisão de privilégios da aplicação.

## Estado atual

O DB01 está com:

```text
Debian 13
PostgreSQL 17.11
IP 10.10.10.30
Porta 5432
Banco linuxinfra
Role linuxinfra_app
SCRAM-SHA-256
```

Clientes autorizados:

```text
APP01 - 10.10.10.21
APP02 - 10.10.10.22
```

A comunicação, autenticação, leitura, escrita e persistência compartilhada foram validadas com sucesso.