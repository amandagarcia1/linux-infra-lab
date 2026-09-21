# Rede Hyper-V

Este documento descreve a arquitetura de rede utilizada pelo laboratório `linux-infra-lab`.

## Objetivo

Criar uma rede virtual isolada para as máquinas do laboratório, permitindo:

- comunicação entre as VMs;
- comunicação entre o host Windows e as VMs;
- endereçamento IP controlado;
- acesso das VMs à internet através de NAT;
- evitar conexão direta das VMs com a interface física do host;
- manter o laboratório independente da rede externa.

## Arquitetura da rede

A rede do laboratório utiliza um switch virtual interno do Hyper-V.

```text
Windows Host
10.10.10.1
     |
     |
vEthernet (LAB-INFRA)
     |
     v
LAB-INFRA
10.10.10.0/24
     |
     +-- PROXY01 - 10.10.10.10
     |
     +-- APP01   - 10.10.10.21
     |
     +-- APP02   - 10.10.10.22
     |
     +-- DB01    - 10.10.10.30
```

O host Windows funciona como gateway da rede do laboratório.

## Switch virtual

Foi criado no Hyper-V o switch:

```text
LAB-INFRA
```

Tipo:

```text
Internal
```

Um switch do tipo `Internal` permite comunicação entre:

```text
Windows Host
     |
     +-- PROXY01
     +-- APP01
     +-- APP02
     +-- DB01
```

As VMs não são conectadas diretamente à interface física de rede do computador.

O acesso externo é realizado através do NAT configurado no Windows.

## Rede utilizada

Rede:

```text
10.10.10.0/24
```

Máscara:

```text
255.255.255.0
```

Prefixo:

```text
/24
```

Faixa de endereços utilizáveis:

```text
10.10.10.1 até 10.10.10.254
```

Broadcast:

```text
10.10.10.255
```

## Endereçamento atual

| Equipamento | Endereço IP | Função |
|---|---|---|
| Windows Host | `10.10.10.1` | Gateway e NAT |
| PROXY01 | `10.10.10.10` | Nginx / Load Balancer |
| APP01 | `10.10.10.21` | FastAPI / Docker |
| APP02 | `10.10.10.22` | FastAPI / Docker |
| DB01 | `10.10.10.30` | PostgreSQL |

Gateway utilizado pelas VMs:

```text
10.10.10.1
```

DNS utilizado inicialmente pelas VMs:

```text
1.1.1.1
```

Domínio utilizado no laboratório:

```text
lab.home.arpa
```

Exemplos:

```text
proxy01.lab.home.arpa
app01.lab.home.arpa
app02.lab.home.arpa
db01.lab.home.arpa
```

## Interface virtual do Windows

Ao criar o switch interno, o Hyper-V criou no Windows a interface:

```text
vEthernet (LAB-INFRA)
```

Essa interface recebeu:

```text
10.10.10.1/24
```

Ela funciona como ponto de comunicação entre o host Windows e a rede virtual.

Fluxo:

```text
Windows Host
     |
     v
vEthernet (LAB-INFRA)
10.10.10.1
     |
     v
LAB-INFRA
10.10.10.0/24
```

## NAT

Foi criado NAT no Windows para permitir que as VMs acessem redes externas.

Nome:

```text
LAB-INFRA-NAT
```

Rede interna:

```text
10.10.10.0/24
```

Fluxo de saída:

```text
VM
 |
 v
10.10.10.1
Windows Host
 |
 v
LAB-INFRA-NAT
 |
 v
Interface externa do host
 |
 v
Internet
```

Exemplo a partir do APP01:

```text
APP01
10.10.10.21
     |
     v
Gateway
10.10.10.1
     |
     v
Windows NAT
     |
     v
Internet
```

O mesmo fluxo é utilizado por:

```text
PROXY01
APP01
APP02
DB01
```

## Comunicação interna

As VMs conseguem se comunicar diretamente utilizando seus endereços da rede `LAB-INFRA`.

Exemplos:

```text
PROXY01
   |
   +----> APP01:8000
   |
   +----> APP02:8000
```

Também:

```text
APP01 ----\
           \
            ---> DB01:5432
           /
APP02 ----/
```

Essa comunicação não depende do NAT.

O NAT é necessário somente quando as VMs precisam acessar redes externas.

## Fluxo da aplicação

A comunicação principal da aplicação ocorre da seguinte forma:

```text
Cliente
   |
   v
PROXY01
10.10.10.10:80
   |
   +------> APP01
   |        10.10.10.21:8000
   |
   +------> APP02
            10.10.10.22:8000
               |
               |
               v
            DB01
        10.10.10.30:5432
```

APP01 e APP02 também acessam diretamente o DB01:

```text
APP01: 10.10.10.21
        |
        +------> DB01:5432

APP02: 10.10.10.22
        |
        +------> DB01:5432
```

## Configuração de rede das VMs

As VMs utilizam configuração IPv4 estática.

Exemplo do APP01:

```text
IP:      10.10.10.21/24
Gateway: 10.10.10.1
DNS:     1.1.1.1
```

Exemplo do APP02:

```text
IP:      10.10.10.22/24
Gateway: 10.10.10.1
DNS:     1.1.1.1
```

Exemplo do PROXY01:

```text
IP:      10.10.10.10/24
Gateway: 10.10.10.1
DNS:     1.1.1.1
```

Exemplo do DB01:

```text
IP:      10.10.10.30/24
Gateway: 10.10.10.1
DNS:     1.1.1.1
```

## Comandos utilizados no Windows

### Criar o switch interno

```powershell
New-VMSwitch `
    -Name "LAB-INFRA" `
    -SwitchType Internal
```

### Configurar o endereço do host

```powershell
New-NetIPAddress `
    -InterfaceAlias "vEthernet (LAB-INFRA)" `
    -IPAddress 10.10.10.1 `
    -PrefixLength 24
```

### Criar o NAT

```powershell
New-NetNat `
    -Name "LAB-INFRA-NAT" `
    -InternalIPInterfaceAddressPrefix "10.10.10.0/24"
```

## Comandos de validação no Windows

### Verificar os switches Hyper-V

```powershell
Get-VMSwitch
```

### Verificar o endereço da interface LAB-INFRA

```powershell
Get-NetIPAddress `
    -InterfaceAlias "vEthernet (LAB-INFRA)" `
    -AddressFamily IPv4
```

### Verificar o NAT

```powershell
Get-NetNat
```

### Verificar adaptadores virtuais

```powershell
Get-NetAdapter
```

## Validações realizadas nas VMs

### Comunicação com o gateway

```bash
ping -c 4 10.10.10.1
```

### Comunicação externa por IP

```bash
ping -c 4 1.1.1.1
```

### Resolução DNS

```bash
ping -c 4 deb.debian.org
```

Esses testes foram validados durante a criação das VMs.

## Testes entre os servidores

### PROXY01 para APP01

```bash
curl http://10.10.10.21:8000
```

### PROXY01 para APP02

```bash
curl http://10.10.10.22:8000
```

Os dois servidores responderam corretamente.

## Comunicação com PostgreSQL

O PostgreSQL no DB01 está disponível em:

```text
10.10.10.30:5432
```

Foram validadas conexões a partir de:

```text
APP01 - 10.10.10.21
APP02 - 10.10.10.22
```

O acesso ao banco foi configurado de forma restritiva, permitindo somente os servidores de aplicação autorizados.

Fluxo:

```text
APP01
10.10.10.21
      \
       \
        ---> DB01
             10.10.10.30:5432
       /
      /
APP02
10.10.10.22
```

## Redes Docker

APP01 e APP02 também possuem redes internas do Docker.

A rede customizada utilizada pela aplicação é:

```text
app-network
```

Essas redes são diferentes da rede Hyper-V.

Exemplo:

```text
Hyper-V
10.10.10.0/24
     |
     v
APP01
10.10.10.21
     |
     v
Docker
app-network
     |
     v
app01-api
```

O container publica a aplicação no endereço da VM:

```text
APP01
10.10.10.21:8000
```

e:

```text
APP02
10.10.10.22:8000
```

## Motivo para utilizar Internal Switch

Foi escolhido um switch Hyper-V do tipo `Internal` para manter maior controle sobre:

- endereçamento;
- comunicação entre as VMs;
- comunicação com o host;
- roteamento;
- NAT;
- isolamento do laboratório.

Não foi necessário conectar cada VM diretamente à interface física do host.

O acesso externo ocorre através do Windows:

```text
VM
 |
 v
LAB-INFRA
 |
 v
Windows Host
 |
 v
NAT
 |
 v
Internet
```

## Estado atual

A rede atualmente suporta:

```text
PROXY01
APP01
APP02
DB01
```

e já foi validada para:

- comunicação entre host e VMs;
- comunicação entre as VMs;
- acesso à internet;
- resolução DNS;
- balanceamento HTTP;
- acesso dos APPs ao PostgreSQL;
- comunicação entre containers e serviços externos ao Docker.

## Evoluções futuras

Conforme o laboratório evoluir, a camada de rede também poderá incluir:

- `PROXY02`;
- `DB02`;
- IP virtual para os proxies;
- Keepalived/VRRP;
- regras de firewall entre os serviços;
- segmentação adicional;
- monitoramento de disponibilidade;
- testes de falha de rede;
- análise de tráfego entre os componentes.