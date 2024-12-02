# Clingo container

This repository contains a Docker environment configured to run Clingo, a system for logic programming and solving problems using Answer Set Programming (ASP).

## Requirements

- Docker
- Docker Compose

Make sure Docker and Docker Compose are installed. You can verify the installation by running:

```bash
docker --version
docker compose --version
```

# Installation guide

1. Clone the repository or download the necessary files.
2. Create a code folder to share files between your local environment and the Docker container:

   ```bash
   mkdir code
   ```

3. Set the permissions for the code folder so it can be accessed by the container:

   ```bash
   chmod 777 code
   ```

## Starting the container

To run Clingo, use the following command:

```bash
docker compose run clingo
```
