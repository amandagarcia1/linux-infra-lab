# Arquitetura Inicial

Este documento descreve a arquitetura inicial do laboratório `linux-infra-lab`.

## Objetivo da arquitetura

O objetivo é construir uma infraestrutura Linux separando as principais funções em máquinas virtuais diferentes.

Cada VM terá um papel específico:

- `PROXY01`: entrada das requisições e balanceamento de carga.
- `APP01`: primeira instância da aplicação.
- `APP02`: segunda instância da aplicação.
- `DB01`: banco de dados PostgreSQL.

## Arquitetura

```text
                    Windows Host
                         |
                      Hyper-V
                         |
                    LAB-INFRA
                   10.10.10.0/24
                         |
          +--------------+--------------+
          |              |              |
       PROXY01          APP01          APP02
     10.10.10.10      10.10.10.21    10.10.10.22
          |              |              |
          |              +------+-------+
          |                     |
          |                    DB01
          |                 10.10.10.30
          |
          +---- Load Balancing

          Papel de cada servidor
PROXY01

Responsável por receber as requisições dos clientes e encaminhá-las para os servidores de aplicação.

Tecnologias previstas:

Debian 13
Nginx
reverse proxy
load balancing
health checks

Futuramente será usado para testar alta disponibilidade e failover.

APP01

Primeiro servidor de aplicação.

Tecnologias:

Debian 13
Docker Engine
aplicação containerizada

IP:

10.10.10.21
APP02

Segundo servidor de aplicação.

Terá praticamente a mesma configuração do APP01.

IP:

10.10.10.22

O objetivo é permitir que a aplicação continue disponível caso um dos servidores deixe de responder.

DB01

Servidor dedicado ao banco de dados.

Tecnologia prevista:

Debian 13
PostgreSQL

IP:

10.10.10.30

As aplicações executadas no APP01 e APP02 irão acessar o mesmo banco de dados.

Fluxo de uma requisição
Cliente
   |
   v
PROXY01
   |
   +------> APP01
   |
   +------> APP02
              |
              v
             DB01

O PROXY01 decidirá para qual servidor de aplicação enviar cada requisição.

Se o APP01 estiver indisponível:

PROXY01
   |
   +------> APP01  X
   |
   +------> APP02  OK

A aplicação deverá continuar disponível pelo APP02.

Evolução prevista

A arquitetura será expandida posteriormente para incluir:

segundo servidor de proxy;
failover do proxy;
PostgreSQL replicado;
Redis;
monitoramento com Prometheus;
dashboards com Grafana;
centralização de logs;
backup;
Ansible;
CI/CD;
testes de falha e recuperação.