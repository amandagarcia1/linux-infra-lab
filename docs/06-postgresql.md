# PostgreSQL

Este documento descreve a instalação, configuração, validação, backup e restauração do PostgreSQL no servidor `DB01`.

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

## Endpoints de leitura e escrita

A aplicação também passou a disponibilizar:

```text
GET /records
POST /records
```

O `GET /records` permite consultar os registros da tabela `lab_test`.

O `POST /records` permite criar registros utilizando a API.

Esses endpoints foram validados em:

```text
APP01
APP02
PROXY01
```

Foi criado um registro diretamente pelo APP01:

```text
id: 3
origem: app01
mensagem: Registro criado pela API no APP01
```

E outro registro através do PROXY01:

```text
id: 4
origem: proxy
mensagem: Registro criado via PROXY01
```

Depois, o `GET /records` executado através do PROXY01 retornou todos os registros do banco.

Isso confirmou o fluxo completo:

```text
Cliente
   |
   v
PROXY01
   |
   v
APP01 ou APP02
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

# Backup e restauração

Foi realizado um teste completo de backup lógico e restauração do banco `linuxinfra`.

O objetivo não foi apenas gerar um arquivo de backup, mas validar que ele poderia ser restaurado corretamente.

## Backup lógico com pg_dump

Foi utilizado o `pg_dump` em formato customizado:

```bash
sudo -u postgres pg_dump \
  -Fc \
  -d linuxinfra \
  -f /tmp/linuxinfra-2026-09-22.dump
```

O parâmetro:

```text
-Fc
```

utiliza o formato customizado do PostgreSQL.

Esse formato é apropriado para uso com `pg_restore` e permite maior flexibilidade durante a restauração, incluindo seleção de objetos do backup.

Depois o arquivo foi movido para:

```text
~/backups/postgresql/linuxinfra-2026-09-22.dump
```

## Inspeção do backup

Antes da restauração, o conteúdo do arquivo foi validado com:

```bash
pg_restore -l \
  ~/backups/postgresql/linuxinfra-2026-09-22.dump
```

O archive continha:

```text
TABLE public lab_test
SEQUENCE public lab_test_id_seq
DEFAULT public lab_test id
TABLE DATA public lab_test
SEQUENCE SET public lab_test_id_seq
CONSTRAINT public lab_test lab_test_pkey
```

Também foi confirmado:

```text
Database: linuxinfra
PostgreSQL: 17.11
Format: CUSTOM
Compression: gzip
```

## Banco temporário de restauração

Para evitar qualquer alteração no banco original, foi criado:

```text
linuxinfra_restore_test
```

com owner:

```text
linuxinfra_app
```

Comando:

```bash
sudo -u postgres createdb \
  -O linuxinfra_app \
  linuxinfra_restore_test
```

Validação:

```bash
sudo -u postgres psql -lqt | grep linuxinfra_restore_test
```

## Permissão para leitura do dump

Durante o primeiro teste, o `pg_restore` executado como usuário `postgres` não conseguiu acessar diretamente o arquivo armazenado dentro do diretório pessoal:

```text
/home/amandasilveira/backups/postgresql/
```

O erro observado foi:

```text
Permission denied
```

Para o teste, o arquivo foi copiado temporariamente para:

```text
/tmp/linuxinfra-2026-09-22.dump
```

e recebeu permissão de leitura:

```bash
cp ~/backups/postgresql/linuxinfra-2026-09-22.dump /tmp/

chmod 644 /tmp/linuxinfra-2026-09-22.dump
```

O backup original foi mantido sem alterações.

## Restauração

O backup foi restaurado no banco temporário utilizando:

```bash
sudo -u postgres pg_restore \
  --exit-on-error \
  -d linuxinfra_restore_test \
  /tmp/linuxinfra-2026-09-22.dump
```

A opção:

```text
--exit-on-error
```

faz o processo interromper caso seja encontrado algum erro durante a restauração.

A restauração foi concluída sem erros.

## Validação dos dados restaurados

Depois da restauração:

```bash
sudo -u postgres psql -d linuxinfra_restore_test
```

Foi executada:

```sql
SELECT id, origem, mensagem, criado_em
FROM lab_test
ORDER BY id;
```

Resultado:

```text
 id | origem |             mensagem
----+--------+-----------------------------------
  1 | app01  | Registro criado pelo APP01
  2 | app02  | Registro criado pelo APP02
  3 | app01  | Registro criado pela API no APP01
  4 | proxy  | Registro criado via PROXY01
```

Os quatro registros existentes no momento do backup foram recuperados corretamente.

## Validação da sequência

Também foi validada a sequência utilizada pela coluna `id`:

```sql
SELECT last_value
FROM lab_test_id_seq;
```

Resultado:

```text
4
```

Isso confirmou que a sequência foi restaurada juntamente com os dados.

## Resultado do teste

O fluxo validado foi:

```text
linuxinfra
    |
    v
pg_dump
    |
    v
arquivo .dump
    |
    v
pg_restore
    |
    v
linuxinfra_restore_test
    |
    v
validação dos dados
```

Foram comprovados:

- geração do backup;
- leitura do archive;
- preservação da estrutura da tabela;
- restauração dos dados;
- restauração da chave primária;
- restauração da sequência;
- recuperação dos registros existentes no momento do backup.

## Limpeza do ambiente de teste

Após a validação, o banco temporário pode ser removido:

```bash
sudo -u postgres dropdb linuxinfra_restore_test
```

E a cópia temporária do arquivo:

```bash
rm /tmp/linuxinfra-2026-09-22.dump
```

O backup original permanece armazenado em:

```text
~/backups/postgresql/linuxinfra-2026-09-22.dump
```

## Considerações importantes

O `pg_dump` realiza backup lógico de um banco individual.

Ele não representa, por si só, uma estratégia completa de alta disponibilidade ou recuperação contínua.

Etapas futuras poderão incluir:

- automatização dos backups;
- política de retenção;
- armazenamento dos backups fora do DB01;
- testes periódicos de restauração;
- backup de roles e objetos globais;
- WAL archiving;
- Point-in-Time Recovery.

## Próxima evolução

As etapas de backup e restauração já foram validadas.

A próxima evolução da camada de banco será:

```text
DB01
  |
  v
DB02
  |
  v
replicação
  |
  v
primary / standby
  |
  v
failover
  |
  v
alta disponibilidade
```

## Evoluções futuras

Estão previstas:

- automatização dos backups;
- política de retenção;
- armazenamento de backups fora do DB01;
- testes periódicos de restauração;
- backup de roles e objetos globais;
- criação do `DB02`;
- replicação PostgreSQL;
- estudo de primary/standby;
- failover;
- avaliação do Patroni;
- connection pooling;
- observabilidade do banco;
- métricas PostgreSQL;
- alertas;
- WAL archiving;
- Point-in-Time Recovery;
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

Atualmente foram validados:

- comunicação e autenticação;
- leitura e escrita;
- persistência compartilhada;
- integração com FastAPI;
- `GET /records`;
- `POST /records`;
- acesso através do PROXY01;
- backup lógico;
- inspeção do backup;
- restauração em banco temporário;
- validação dos dados restaurados;
- validação da sequência.

O próximo objetivo da camada de banco é implementar um segundo servidor PostgreSQL e estudar replicação e failover.