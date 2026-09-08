# Rede do Hyper-V

Este documento descreve a rede utilizada pelo laboratório `linux-infra-lab`.

## Objetivo

Criar uma rede isolada para as máquinas virtuais do laboratório, permitindo:

- comunicação entre as VMs;
- comunicação entre o Windows host e as VMs;
- acesso das VMs à internet via NAT;
- evitar conexão direta das VMs com a rede corporativa.

## Switch virtual

Foi criado um switch interno no Hyper-V chamado:

```text
LAB-INFRA
```

Tipo:

```text
Internal
```

Esse tipo de switch permite comunicação entre:

```text
Windows Host
     |
     +-- PROXY01
     +-- APP01
     +-- APP02
     +-- DB01
```

As VMs não ficam diretamente conectadas à placa de rede física do computador.

## Rede utilizada

```text
10.10.10.0/24
```

Máscara:

```text
255.255.255.0
```

Faixa utilizável:

```text
10.10.10.1 até 10.10.10.254
```

## Endereçamento

| Equipamento | IP |
|---|---|
| Windows Host | 10.10.10.1 |
| PROXY01 | 10.10.10.10 |
| APP01 | 10.10.10.21 |
| APP02 | 10.10.10.22 |
| DB01 | 10.10.10.30 |

Gateway das VMs:

```text
10.10.10.1
```

## Interface virtual do Windows

Ao criar o switch interno, o Hyper-V criou no Windows uma interface chamada:

```text
vEthernet (LAB-INFRA)
```

Essa interface recebeu o endereço:

```text
10.10.10.1/24
```

## NAT

Foi criado um NAT no Windows para permitir que as VMs tenham acesso à internet.

Nome:

```text
LAB-INFRA-NAT
```

Rede interna:

```text
10.10.10.0/24
```

Fluxo:

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
Rede externa
     |
     v
Internet
```

## Comandos utilizados no Windows

Criação do switch:

```powershell
New-VMSwitch -Name "LAB-INFRA" -SwitchType Internal
```

Configuração do IP do host:

```powershell
New-NetIPAddress `
    -InterfaceAlias "vEthernet (LAB-INFRA)" `
    -IPAddress 10.10.10.1 `
    -PrefixLength 24
```

Criação do NAT:

```powershell
New-NetNat `
    -Name "LAB-INFRA-NAT" `
    -InternalIPInterfaceAddressPrefix "10.10.10.0/24"
```

## Validações utilizadas

Verificar switches:

```powershell
Get-VMSwitch
```

Verificar IP da interface:

```powershell
Get-NetIPAddress `
    -InterfaceAlias "vEthernet (LAB-INFRA)" `
    -AddressFamily IPv4
```

Verificar NAT:

```powershell
Get-NetNat
```

## Testes realizados no APP01

Teste de comunicação com o host:

```bash
ping -c 4 10.10.10.1
```

Teste de saída para internet:

```bash
ping -c 4 1.1.1.1
```

Teste de DNS:

```bash
ping -c 4 deb.debian.org
```

Todos os testes foram concluídos com sucesso.

## Motivo para não utilizar External Switch

O computador utilizado no laboratório está conectado a uma rede corporativa.

Por esse motivo, as VMs não foram conectadas diretamente à rede física da empresa.

A arquitetura escolhida mantém o laboratório isolado:

```text
Rede corporativa
       |
Windows Host
       |
      NAT
       |
LAB-INFRA
       |
       +-- PROXY01
       +-- APP01
       +-- APP02
       +-- DB01
```

Isso reduz o risco de interferência na rede corporativa e mantém o laboratório controlado.