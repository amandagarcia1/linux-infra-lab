# APP01 - Debian 13

Este documento descreve a criação e configuração inicial do servidor `APP01`.

## Função

O `APP01` é o primeiro servidor de aplicação do laboratório.

Ele será responsável por executar aplicações containerizadas utilizando Docker.

## Configuração da VM

```text
Hostname: app01
FQDN: app01.lab.home.arpa

Sistema operacional: Debian GNU/Linux 13 (Trixie)

vCPU: 2

Memória:
- Inicial: 2048 MB
- Mínima: 1024 MB
- Máxima: 4096 MB
- Memória dinâmica habilitada

Disco:
- VHDX dinâmico
- 20 GB

Rede:
- Hyper-V Switch: LAB-INFRA
- IP: 10.10.10.21/24
- Gateway: 10.10.10.1
- DNS: 1.1.1.1
```

## Particionamento

Foi utilizado o esquema simples com os arquivos do sistema na partição raiz.

```text
/
├── /etc
├── /home
├── /usr
├── /var
└── /srv
```

Essa escolha evita criar limites pequenos em `/var`, diretório que futuramente também armazenará dados do Docker.

## Usuário

Usuário administrativo criado:

```text
amandasilveira
```

O pacote `sudo` foi instalado e o usuário foi adicionado ao grupo `sudo`.

```bash
su -

apt update
apt install sudo

usermod -aG sudo amandasilveira
```

A associação ao novo grupo passou a valer após um novo login.

Validação:

```bash
groups
sudo whoami
```

Resultado esperado:

```text
root
```

## Atualização do sistema

O sistema foi atualizado após a instalação:

```bash
sudo apt update
sudo apt full-upgrade -y
```

Depois:

```bash
sudo reboot
```

## SSH

O servidor OpenSSH foi instalado durante a instalação do Debian.

Validação:

```bash
systemctl status ssh
```

O serviço deve aparecer como:

```text
active (running)
```

## Acesso remoto

O acesso ao servidor é realizado a partir do host Windows:

```powershell
ssh amandasilveira@10.10.10.21
```

## Autenticação por chave SSH

Foi criada uma chave ED25519 no Windows:

```powershell
ssh-keygen -t ed25519 -C "amandasilveira@linux-infra-lab"
```

Arquivos gerados:

```text
id_ed25519
id_ed25519.pub
```

A chave privada permanece somente no computador cliente.

A chave pública foi adicionada ao servidor em:

```text
~/.ssh/authorized_keys
```

## Hardening do SSH

Foi criado o arquivo:

```text
/etc/ssh/sshd_config.d/99-lab-hardening.conf
```

Com:

```text
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
```

Isso impede:

- login direto como root;
- autenticação SSH por senha.

O acesso passa a ser realizado por chave pública.

Antes de aplicar a configuração, a sintaxe foi validada:

```bash
sudo sshd -t
```

A configuração efetiva foi conferida com:

```bash
sudo sshd -T | grep -E 'permitrootlogin|passwordauthentication|pubkeyauthentication'
```

Resultado esperado:

```text
permitrootlogin no
passwordauthentication no
pubkeyauthentication yes
```

Depois a configuração foi aplicada:

```bash
sudo systemctl reload ssh
```

Uma segunda sessão SSH foi aberta antes de encerrar a sessão existente para confirmar que o acesso por chave continuava funcionando.

## Validação de rede

IP:

```bash
ip addr
```

Rota:

```bash
ip route
```

DNS:

```bash
cat /etc/resolv.conf
```

Comunicação com o gateway:

```bash
ping -c 4 10.10.10.1
```

Teste de internet:

```bash
ping -c 4 1.1.1.1
```

Teste de DNS:

```bash
ping -c 4 deb.debian.org
```

Todos os testes foram concluídos com sucesso.

## Validação de recursos

CPU:

```bash
nproc
```

Resultado:

```text
2
```

Memória:

```bash
free -h
```

Resultado aproximado:

```text
1.9 GiB
```

Disco:

```bash
df -h /
```

A partição raiz possui aproximadamente 18 GB disponíveis para o sistema e os serviços.

## Estado atual

O `APP01` está com:

- Debian 13 instalado;
- rede configurada;
- acesso à internet;
- usuário administrativo com sudo;
- SSH ativo;
- autenticação SSH por chave;
- login SSH por senha desabilitado;
- login SSH de root desabilitado;
- sistema atualizado;
- Docker Engine instalado.
