# Docker Básico

Este documento registra os primeiros testes realizados com Docker no `APP01`.

## Instalação

O Docker Engine foi instalado a partir do repositório oficial da Docker para Debian 13.

Pacotes instalados:

```text
docker-ce
docker-ce-cli
containerd.io
docker-buildx-plugin
docker-compose-plugin
```

## Validação do serviço

O serviço foi validado com:

```bash
sudo systemctl status docker
```

E as versões com:

```bash
docker --version
docker compose version
```

## Primeiro container

Foi executado o container oficial de teste:

```bash
sudo docker run hello-world
```

O fluxo observado foi:

```text
Docker CLI
    |
    v
Docker daemon
    |
    +-- procura a imagem localmente
    |
    +-- baixa do registry se necessário
    |
    +-- cria o container
    |
    +-- executa o processo
    |
    +-- encerra o container
```

## Imagem x Container

Imagem:

```text
modelo imutável usado para criar containers
```

Container:

```text
instância executável criada a partir de uma imagem
```

Comandos utilizados:

```bash
sudo docker images
sudo docker ps
sudo docker ps -a
```

`docker ps` mostra apenas containers em execução.

`docker ps -a` também mostra containers finalizados.

## Nginx em container

Foi criado um container Nginx:

```bash
sudo docker run -d \
  --name nginx-lab \
  -p 10.10.10.21:8080:80 \
  nginx:alpine
```

A publicação da porta ficou:

```text
APP01
10.10.10.21:8080
        |
        v
Docker
        |
        v
nginx-lab:80
```

O acesso foi validado com:

```bash
curl http://10.10.10.21:8080
```

## Rede padrão do Docker

As redes iniciais foram verificadas com:

```bash
sudo docker network ls
```

Redes encontradas:

```text
bridge
host
none
```

O container `nginx-lab` recebeu inicialmente um endereço na rede `bridge`:

```text
172.17.0.2
```

## Rede Docker customizada

Foi criada uma rede própria:

```bash
sudo docker network create app-network
```

Depois o container foi conectado a ela:

```bash
sudo docker network connect app-network nginx-lab
```

O novo endereço interno recebido foi:

```text
172.18.0.2
```

O container ficou temporariamente conectado a duas redes:

```text
nginx-lab
├── bridge
│   └── 172.17.0.2
└── app-network
    └── 172.18.0.2
```

Depois ele foi removido da bridge padrão:

```bash
sudo docker network disconnect bridge nginx-lab
```

Estado final:

```text
nginx-lab
└── app-network
    └── 172.18.0.2
```

## DNS interno do Docker

Containers conectados à mesma rede customizada conseguem resolver uns aos outros por nome.

Isso foi testado com um container temporário:

```bash
sudo docker run --rm \
  --network app-network \
  curlimages/curl \
  http://nginx-lab
```

Nesse cenário:

```text
container temporário
        |
        | nginx-lab
        v
DNS interno Docker
        |
        v
172.18.0.2
        |
        v
nginx-lab:80
```

O acesso funcionou sem utilizar diretamente o IP interno do container.

## Container temporário

A opção:

```text
--rm
```

faz com que o container seja removido automaticamente após terminar sua execução.

Isso foi validado com:

```bash
sudo docker ps -a
```

O container temporário não permaneceu listado após finalizar.

## Estado atual

No `APP01` temos:

- Docker Engine ativo;
- Docker Compose disponível;
- imagem `hello-world`;
- container `nginx-lab`;
- rede customizada `app-network`;
- Nginx acessível pela porta `8080`;
- comunicação entre containers por DNS interno validada.

## Próximos passos

A próxima etapa será criar uma aplicação própria, gerar uma imagem com `Dockerfile` e executá-la no `APP01`.