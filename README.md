# Linux Infra Lab

Laboratório prático de infraestrutura Linux com foco em aprimoramento de:

- Linux
- Hyper-V
- redes
- SSH
- Docker
- Nginx
- PostgreSQL
- load balancing
- failover
- observabilidade
- segurança
- automação

## Arquitetura inicial

O laboratório roda em Hyper-V usando uma rede interna isolada da rede corporativa.

```text
Windows Host
    |
    | NAT
    |
LAB-INFRA - 10.10.10.0/24
    |
    +-- PROXY01 - 10.10.10.10
    |
    +-- APP01   - 10.10.10.21
    |
    +-- APP02   - 10.10.10.22
    |
    +-- DB01    - 10.10.10.30
```

    Status

- [x] Criar rede LAB-INFRA no Hyper-V
- [x] Configurar NAT
- [x] Criar APP01
- [x] Instalar Debian 13
- [x] Configurar SSH
- [x] Configurar autenticação SSH por chave
- [x] Instalar Docker Engine
- [x] Criar rede Docker customizada
- [x] Executar Nginx em container
- [ ] Criar aplicação própria
- [ ] Criar Dockerfile
- [ ] Criar APP02
- [ ] Criar PROXY01
- [ ] Configurar load balancing
- [ ] Testar failover
- [ ] Criar DB01
- [ ] Configurar PostgreSQL



## Documentação

- [Arquitetura inicial](docs/01-architecture.md)
- [Rede Hyper-V](docs/02-hyperv-network.md)
- [APP01 - Debian](docs/03-app01-debian.md)
- [Docker básico](docs/04-docker-basics.md)

## Objetivo

O objetivo deste projeto é construir uma infraestrutura Linux do zero e entender cada componente antes de adicionar camadas de automação.

O laboratório será evoluído gradualmente para incluir alta disponibilidade, monitoramento, logs centralizados, automação e testes de falha.
