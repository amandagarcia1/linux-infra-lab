# Nginx - Load Balancing e Failover

Este documento descreve a configuração do `PROXY01` utilizando Nginx como reverse proxy e load balancer entre `APP01` e `APP02`.

## Objetivo

Disponibilizar um único ponto de entrada para a aplicação e distribuir as requisições entre duas instâncias independentes da FastAPI.

Arquitetura:

```text
Cliente
   |
   v
PROXY01
10.10.10.10
Nginx
   |
   +----------> APP01
   |           10.10.10.21:8000
   |
   +----------> APP02
               10.10.10.22:8000
```

## PROXY01

Identificação:

```text
Hostname: proxy01
IP: 10.10.10.10
Sistema operacional: Debian 13
```

Função:

```text
Reverse Proxy
Load Balancer
```

O Nginx foi instalado diretamente no sistema operacional do `PROXY01`.

## Backends

Os servidores de aplicação utilizados pelo Nginx são:

```text
APP01
10.10.10.21:8000

APP02
10.10.10.22:8000
```

Os dois executam a mesma aplicação FastAPI em containers Docker.

## Teste dos backends antes do balanceamento

Antes de configurar o Nginx, foi validado que o `PROXY01` conseguia acessar diretamente os dois servidores.

APP01:

```bash
curl http://10.10.10.21:8000
```

APP02:

```bash
curl http://10.10.10.22:8000
```

As duas aplicações responderam corretamente.

## Arquivo de configuração

A configuração foi criada em:

```text
/etc/nginx/sites-available/linux-infra-lab
```

Configuração atual:

```nginx
upstream app_backend {
    server 10.10.10.21:8000 max_fails=2 fail_timeout=10s;
    server 10.10.10.22:8000 max_fails=2 fail_timeout=10s;
}

server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://app_backend;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Upstream

O bloco:

```nginx
upstream app_backend {
    server 10.10.10.21:8000 max_fails=2 fail_timeout=10s;
    server 10.10.10.22:8000 max_fails=2 fail_timeout=10s;
}
```

define o grupo de servidores chamado:

```text
app_backend
```

Esse grupo possui:

```text
APP01
APP02
```

Como nenhum outro algoritmo foi configurado, o Nginx utiliza o método padrão de balanceamento `round-robin`. :contentReference[oaicite:0]{index=0}

Fluxo:

```text
requisição 1 -> APP01
requisição 2 -> APP02
requisição 3 -> APP01
requisição 4 -> APP02
```

Na prática, a distribuição pode variar conforme disponibilidade e falhas dos servidores.

## Reverse proxy

O trecho:

```nginx
location / {
    proxy_pass http://app_backend;
}
```

faz com que as requisições recebidas pelo `PROXY01` sejam encaminhadas para o grupo:

```text
app_backend
```

Fluxo:

```text
Cliente
   |
   v
10.10.10.10:80
   |
   v
Nginx
   |
   v
app_backend
   |
   +--> APP01
   |
   +--> APP02
```

## Headers encaminhados

Foram configurados:

```nginx
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

Esses headers permitem preservar informações da requisição original ao encaminhá-la para os servidores de aplicação.

Entre elas:

```text
Host original
IP do cliente
cadeia de proxies
protocolo utilizado
```

## Detecção passiva de falhas

Cada backend foi configurado com:

```text
max_fails=2
fail_timeout=10s
```

Exemplo:

```nginx
server 10.10.10.21:8000 max_fails=2 fail_timeout=10s;
```

O parâmetro `max_fails=2` define o número de tentativas malsucedidas necessárias para que o backend seja considerado temporariamente indisponível.

O `fail_timeout=10s` define tanto a janela em que essas falhas são contabilizadas quanto o período em que o servidor pode ser tratado como indisponível. :contentReference[oaicite:1]{index=1}

## Importante: health check passivo

O mecanismo utilizado atualmente é passivo.

Isso significa que o Nginx identifica a falha durante requisições reais.

Fluxo:

```text
Cliente
   |
   v
Nginx
   |
   v
APP01
   |
   X falha
   |
   v
Nginx tenta outro backend
   |
   v
APP02
```

Não existe atualmente um processo independente consultando periodicamente:

```text
/health
```

ou:

```text
/health/db
```

para decidir previamente se o backend está saudável.

## Health check ativo

O endpoint:

```text
/health
```

existe na aplicação, mas atualmente não é utilizado pelo Nginx para health check ativo.

Também existe:

```text
/health/db
```

que valida a comunicação da aplicação com PostgreSQL.

Esses endpoints poderão ser utilizados futuramente por ferramentas de observabilidade ou mecanismos adicionais de health checking.

O módulo nativo `health_check` documentado pelo Nginx para checks periódicos faz parte do NGINX Plus. :contentReference[oaicite:2]{index=2}

## Ativação da configuração

O site padrão foi removido:

```bash
sudo rm /etc/nginx/sites-enabled/default
```

Depois foi criado o link simbólico:

```bash
sudo ln -s \
  /etc/nginx/sites-available/linux-infra-lab \
  /etc/nginx/sites-enabled/linux-infra-lab
```

## Validação da configuração

Antes de aplicar qualquer alteração:

```bash
sudo nginx -t
```

Resultado esperado:

```text
syntax is ok
test is successful
```

Depois:

```bash
sudo systemctl reload nginx
```

## Teste do balanceamento

O teste foi realizado acessando:

```bash
curl http://10.10.10.10
```

As respostas alternaram entre:

```json
{
  "app": "linux-infra-lab",
  "hostname": "app01",
  "status": "ok"
}
```

e:

```json
{
  "app": "linux-infra-lab",
  "hostname": "app02",
  "status": "ok"
}
```

Isso confirmou que os dois backends estavam participando do balanceamento.

## Teste pelo Windows

O mesmo teste também pode ser realizado pelo host:

```powershell
curl.exe http://10.10.10.10
```

Fluxo:

```text
Windows Host
     |
     v
PROXY01
     |
     +------> APP01
     |
     +------> APP02
```

## Teste de failover

Para validar a continuidade do serviço, o container do APP01 foi interrompido:

```bash
sudo docker stop app01-api
```

Arquitetura durante o teste:

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

As requisições continuaram sendo respondidas pelo APP02.

## Recuperação do APP01

O container foi iniciado novamente:

```bash
sudo docker start app01-api
```

Depois disso, as requisições voltaram a ser distribuídas entre:

```text
APP01
APP02
```

## Resultado do teste

O laboratório comprovou:

- funcionamento do reverse proxy;
- distribuição de requisições;
- uso de dois backends;
- detecção passiva de falhas;
- continuidade do serviço com uma instância de aplicação indisponível;
- retorno automático do backend após sua recuperação.

## Integração atual com PostgreSQL

APP01 e APP02 agora também possuem acesso ao mesmo PostgreSQL.

Arquitetura atual completa:

```text
Cliente
   |
   v
PROXY01
Nginx
   |
   +----------> APP01
   |             |
   |             v
   |           Psycopg
   |             |
   +----------> APP02
                 |
                 v
               Psycopg
                 |
                 v
                DB01
             PostgreSQL
```

A disponibilidade da camada HTTP não garante, sozinha, disponibilidade completa da aplicação.

Por exemplo:

```text
APP01 OK
APP02 OK
DB01 X
```

Nesse cenário, os servidores de aplicação continuam ativos, mas operações dependentes do banco podem falhar.

Por isso foi criado também:

```text
GET /health/db
```

para verificar a comunicação da aplicação com PostgreSQL.

## Ponto único de falha atual

Atualmente existe apenas:

```text
PROXY01
```

Se ele ficar indisponível:

```text
Cliente
   |
   X
PROXY01
```

APP01 e APP02 podem continuar ativos, porém o ponto principal de entrada ficará indisponível.

Portanto, o `PROXY01` ainda é um:

```text
Single Point of Failure
```

## Evolução futura do proxy

Está planejada a criação de:

```text
PROXY02
```

Arquitetura futura:

```text
             IP Virtual
                 |
        +--------+--------+
        |                 |
        v                 v
     PROXY01           PROXY02
        |                 |
        +--------+--------+
                 |
          +------+------+
          |             |
          v             v
        APP01         APP02
```

A ideia é estudar:

- redundância de proxy;
- Keepalived;
- VRRP;
- IP virtual;
- failover entre proxies.

## Evoluções futuras

Além da redundância do proxy, poderão ser adicionados:

- observabilidade do Nginx;
- métricas;
- logs centralizados;
- alertas;
- testes automatizados de indisponibilidade;
- monitoramento dos endpoints `/health`;
- monitoramento de `/health/db`;
- TLS/HTTPS;
- regras adicionais de timeout;
- connection limits;
- testes de comportamento durante falhas do PostgreSQL.

## Estado atual

O `PROXY01` está com:

```text
Nginx
Reverse Proxy
Load Balancing
Round Robin
Detecção passiva de falhas
```

Backends:

```text
APP01 - 10.10.10.21:8000
APP02 - 10.10.10.22:8000
```

Configuração atual:

```nginx
upstream app_backend {
    server 10.10.10.21:8000 max_fails=2 fail_timeout=10s;
    server 10.10.10.22:8000 max_fails=2 fail_timeout=10s;
}
```

O balanceamento e o failover da camada de aplicação foram validados com sucesso.