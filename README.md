# Templete FastAPi by Brandon M.

Templete para projecto de Api con FastApi, integrando funcionalidad de envio de email, token con JWT, y sistema gestión de permisos.

- FastApi
- MySql | Postgress | (SQL)

## Installation

##### Requisitos previos:

- Instalar python 3.8+
- Instalar MySql
- Configurar variables de entorno en .env

Instalar dependencias y correr servicio.

```sh
cd templete_fastapi
python -m venv venv
pip install -r requeriments.txt
source venv/bin/activate
uvicorn app:app --reload
```

Para correr servicio con Ngrok server.

```sh
USE_NGROK=True uvicorn server:app
uvicorn app:app --reload
```
