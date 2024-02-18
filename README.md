# Apache Airflow - Estudo



## Sobre este repositório
Em manutenção

### Instalação e Configuração

1. Cria estrura do projeto Apache Airflow:
```bash
astro dev init
```

2. Inicializa serviço do airflow no docker :
```bash
astro dev start
```

3. Lista as redes docker :
```bash
docker network ls
```
4. Rede docker: Copia rede do airflow `id_rede_docker`

5. Cria container `postgres-container` :
```bash
cd postgres-container

docker run --network <id_rede_docker> --name postgres-container -p 5433:5432 -e POSTGRES_USER=admindb -e POSTGRES_PASSWORD=admindb123 -e POSTGRES_DB=astrodb -v ./volumes/postgres/data:/var/lib/postgresql/data -d postgres:12.6
```

6. Cria container `minio-container`
```bash
cd minio-container
docker docker compose up -d
```
