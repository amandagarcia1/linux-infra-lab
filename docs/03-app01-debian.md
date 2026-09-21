# APP01 - Debian 13

Este documento descreve a criação, configuração e evolução do servidor `APP01`.

## Função

O `APP01` é o primeiro servidor de aplicação do laboratório.

Ele é responsável por executar a aplicação FastAPI em container Docker e se comunicar com o banco PostgreSQL hospedado no `DB01`.

Fluxo atual:

```text
Cliente
   |
   v
PROXY01
   |
   v
APP01
Docker
FastAPI
Psycopg
   |
   v
DB01
PostgreSQL
```

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

Essa escolha evita criar limites pequenos em `/var`, diretório utilizado também pelo Docker em:

```text
/var/lib/docker
```

## Usuário administrativo

Usuário criado:

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

A associação ao grupo passou a valer após novo login.

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

Após a instalação, o sistema foi atualizado:

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

Estado esperado:

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

Foi criado:

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

O acesso passa a utilizar autenticação por chave pública.

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

Depois:

```bash
sudo systemctl reload ssh
```

Uma segunda sessão SSH foi aberta antes de encerrar a sessão existente para confirmar que o acesso por chave continuava funcionando.

## Validação de rede

### Endereço IP

```bash
ip addr
```

### Rotas

```bash
ip route
```

### DNS

```bash
cat /etc/resolv.conf
```

### Comunicação com o gateway

```bash
ping -c 4 10.10.10.1
```

### Acesso externo

```bash
ping -c 4 1.1.1.1
```

### Resolução DNS

```bash
ping -c 4 deb.debian.org
```

Todos os testes foram concluídos com sucesso.

## Validação de recursos

### CPU

```bash
nproc
```

Resultado:

```text
2
```

### Memória

```bash
free -h
```

Resultado aproximado:

```text
1.9 GiB
```

### Disco

```bash
df -h /
```

A partição raiz possui aproximadamente 18 GB utilizáveis pelo sistema e pelos serviços.

## Docker Engine

O Docker Engine foi instalado utilizando o repositório oficial do Docker.

Componentes instalados:

```text
docker-ce
docker-ce-cli
containerd.io
docker-buildx-plugin
docker-compose-plugin
```

A instalação foi validada inicialmente com:

```bash
sudo docker run hello-world
```

## Rede Docker

Foi criada uma rede bridge customizada:

```text
app-network
```

Essa rede é utilizada pelo container da aplicação.

Exemplo:

```text
APP01
10.10.10.21
   |
   v
Docker
   |
app-network
   |
   v
app01-api
```

A rede Docker é independente da rede Hyper-V `10.10.10.0/24`.

## Aplicação FastAPI

O servidor executa uma aplicação própria desenvolvida em FastAPI.

A aplicação está localizada no repositório:

```text
~/linux-infra-lab/app
```

Arquivos principais:

```text
app/
├── app.py
├── Dockerfile
├── requirements.txt
├── .dockerignore
└── .env
```

O arquivo `.env` é local e não é versionado no Git.

## Imagem Docker

A primeira versão utilizada foi:

```text
linux-infra-app:1.0
```

Após a integração com PostgreSQL, foi criada:

```text
linux-infra-app:1.1
```

A versão atual do APP01 é:

```text
linux-infra-app:1.1
```

## Container da aplicação

Nome:

```text
app01-api
```

Hostname interno:

```text
app01
```

Rede:

```text
app-network
```

Porta publicada:

```text
10.10.10.21:8000
```

Comando utilizado:

```bash
sudo docker run -d \
  --name app01-api \
  --hostname app01 \
  --network app-network \
  --env-file .env \
  --restart unless-stopped \
  -p 10.10.10.21:8000:8000 \
  linux-infra-app:1.1
```

## Política de restart

O container utiliza:

```text
unless-stopped
```

Isso permite que o container seja iniciado automaticamente após reinicialização do Docker ou da VM, exceto quando tiver sido explicitamente parado.

## Variáveis de ambiente

A aplicação recebe a configuração do PostgreSQL através de:

```text
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
```

Exemplo de estrutura do `.env`:

```text
DB_HOST=10.10.10.30
DB_PORT=5432
DB_NAME=linuxinfra
DB_USER=linuxinfra_app
DB_PASSWORD=<senha>
```

O arquivo:

```text
.env
```

possui permissão restrita:

```bash
chmod 600 .env
```

e não é versionado no Git.

## Dockerignore

O `.dockerignore` evita que arquivos desnecessários ou sensíveis sejam enviados ao contexto de build.

Conteúdo atual:

```text
.venv
__pycache__
*.pyc
.git
.gitignore
.env
.env.*
```

## Dependências Python

O `requirements.txt` contém atualmente:

```text
fastapi
uvicorn
psycopg[binary]
```

O Psycopg é utilizado pela aplicação para comunicação com PostgreSQL.

## PostgreSQL Client

O cliente PostgreSQL foi instalado no APP01:

```bash
sudo apt install -y postgresql-client
```

Ele foi utilizado para testar diretamente a comunicação com o DB01:

```bash
psql -h 10.10.10.30 -U linuxinfra_app -d linuxinfra
```

A conexão foi validada com sucesso.

## Integração com DB01

O APP01 acessa:

```text
DB01
10.10.10.30:5432
```

Banco:

```text
linuxinfra
```

Role:

```text
linuxinfra_app
```

O acesso foi permitido no PostgreSQL somente para os IPs autorizados.

Para o APP01:

```text
10.10.10.21/32
```

## Teste manual do banco

A conexão foi validada com:

```bash
psql -h 10.10.10.30 -U linuxinfra_app -d linuxinfra
```

E:

```sql
SELECT current_database(), current_user;
```

Resultado:

```text
linuxinfra
linuxinfra_app
```

Também foi criado um registro de teste:

```text
origem: app01
mensagem: Registro criado pelo APP01
```

Esse registro posteriormente foi visualizado pelo APP02, comprovando que ambos utilizam o mesmo banco.

## Integração FastAPI + Psycopg

A aplicação utiliza o Psycopg para abrir conexão com PostgreSQL.

Fluxo:

```text
FastAPI
   |
   v
Psycopg
   |
   v
DB01
PostgreSQL
```

A configuração é obtida através de variáveis de ambiente.

## Endpoint principal

Teste:

```bash
curl http://10.10.10.21:8000/
```

Resposta esperada:

```json
{
  "app": "linux-infra-lab",
  "hostname": "app01",
  "status": "ok"
}
```

## Health check da aplicação

Endpoint:

```text
GET /health
```

Exemplo:

```bash
curl http://10.10.10.21:8000/health
```

## Health check do banco

Foi criado:

```text
GET /health/db
```

Teste:

```bash
curl http://10.10.10.21:8000/health/db
```

Resposta validada:

```json
{
  "status": "healthy",
  "database": "connected",
  "hostname": "app01"
}
```

Esse endpoint valida a cadeia:

```text
HTTP
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

## Participação no balanceamento

O APP01 é um dos backends utilizados pelo Nginx no PROXY01.

Fluxo:

```text
PROXY01
   |
   +------> APP01
   |
   +------> APP02
```

O APP01 atende atualmente em:

```text
10.10.10.21:8000
```

## Teste de failover

O container do APP01 já foi interrompido propositalmente:

```bash
sudo docker stop app01-api
```

Durante esse período, o PROXY01 continuou atendendo através do APP02.

Depois:

```bash
sudo docker start app01-api
```

O APP01 voltou a participar do balanceamento.

## Estado atual

O APP01 está com:

- Debian 13 instalado;
- rede estática configurada;
- acesso à internet;
- usuário administrativo com sudo;
- SSH ativo;
- autenticação SSH por chave;
- login SSH por senha desabilitado;
- login SSH de root desabilitado;
- Docker Engine instalado;
- rede Docker `app-network`;
- aplicação FastAPI em container;
- imagem `linux-infra-app:1.1`;
- restart policy `unless-stopped`;
- Psycopg 3 instalado na imagem;
- PostgreSQL Client instalado;
- acesso ao DB01 validado;
- conexão FastAPI → Psycopg → PostgreSQL validada;
- participação no load balancing do PROXY01;
- failover da camada de aplicação testado.

## Próximas evoluções

As próximas etapas relacionadas ao APP01 incluem:

- implementar `GET /records`;
- implementar `POST /records`;
- testar leitura e escrita através do PROXY01;
- evoluir o gerenciamento de conexões PostgreSQL;
- estudar connection pooling;
- adicionar métricas;
- integrar observabilidade;
- automatizar build e deploy;
- incluir o APP01 em futuros testes de falha controlada.