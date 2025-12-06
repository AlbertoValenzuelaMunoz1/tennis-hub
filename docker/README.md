# Docker: configuraciones disponibles

## Configuraciones base (UVLHub)

- **Desarrollo** (`docker-compose.dev.yml`): build local (`Dockerfile.dev`), bind mount del repo, MariaDB propia, Selenium Grid (hub + chrome + firefox), nginx en 80 → proxy a `web:5000`.
- **Producción** (`docker-compose.prod.yml`): imagen `<your_dockerhub_name>/uvlhub:latest`, MariaDB oficial, nginx en 80, watchtower para auto-update.
- **Producción con SSL** (`docker-compose.prod.ssl.yml`): igual que prod, pero nginx expone 80/443, monta `letsencrypt/` y `public/`, añade `certbot`.
- **Producción con webhook** (`docker-compose.prod.webhook.yml`): igual que prod (sin SSL) pero `web` se construye con `Dockerfile.webhook`, monta el repo y el socket de Docker para auto-actualizar vía scripts.
- **Render** (`docker/images/Dockerfile.render`): imagen para despliegue en Render (puerto 80, entrypoint `render_entrypoint.sh`, ignora módulo `webhook`).

## Configuración añadida (TennisHub)

- **Staging** (`docker-compose.staging.yml`): igual que prod pero con `FLASK_ENV=staging`, `LOG_LEVEL=debug`, expone también el puerto 5000 directo para depurar, incluye healthchecks y límites de logs.

## Cómo lanzar

Antes de cualquier entorno, asegúrate de tener `.env` (y `.env.selenium` si usas Selenium) en la raíz del proyecto.

- Desarrollo: `docker compose -f docker/docker-compose.dev.yml up -d --build`
- Producción: `docker compose -f docker/docker-compose.prod.yml up -d`
- Producción SSL: `docker compose -f docker/docker-compose.prod.ssl.yml up -d` (requiere certificados en `docker/letsencrypt` y `public`)
- Producción webhook: `docker compose -f docker/docker-compose.prod.webhook.yml up -d --build`
- Staging (TennisHub): `docker compose -f docker/docker-compose.staging.yml up -d`

Logs y gestión:
- Ver logs: `docker logs <nombre_contenedor>` (p.ej. `web_app_container`, `mariadb_container`, `nginx_web_server_container`)
- Parar entorno: `docker compose -f <archivo> down`
