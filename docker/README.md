# Docker: configuraciones disponibles

## Configuraciones base (UVLHub)

- **Desarrollo** (`docker-compose.dev.yml`): build local (`Dockerfile.dev`), bind mount del repo, MariaDB propia, Selenium Grid (hub + chrome + firefox), nginx en 80 → proxy a `web:5000`.
- **Producción** (`docker-compose.prod.yml`): imagen `<your_dockerhub_name>/uvlhub:latest`, MariaDB oficial, nginx en 80, watchtower para auto-update.
- **Producción con SSL** (`docker-compose.prod.ssl.yml`): igual que prod, pero nginx expone 80/443, monta `letsencrypt/` y `public/`, añade `certbot`.
- **Producción con webhook** (`docker-compose.prod.webhook.yml`): igual que prod (sin SSL) pero `web` se construye con `Dockerfile.webhook`, monta el repo y el socket de Docker para auto-actualizar vía scripts.
- **Render** (`docker/images/Dockerfile.render`): imagen para despliegue en Render (puerto 80, entrypoint `render_entrypoint.sh`, ignora módulo `webhook`).

## Configuración añadida (TennisHub)

- **Staging** (`docker-compose.staging.yml`): Entorno de pre-producción diseñado para validar cambios antes del despliegue final. Características principales:
  - **Healthchecks activos**: Monitorización de la salud de todos los servicios (web, base de datos, nginx) para garantizar su correcto funcionamiento.
  - **Integración con Locust**: Permite realizar pruebas de carga mediante el profile `testing`. Accesible en http://localhost:8089.
  - **Soporte para feature flags**: Variables de entorno configurables (`FEATURE_FLAGS_ENABLED`, `PERFORMANCE_MONITORING`) para activar funcionalidades experimentales.
  - **Gestión optimizada de logs**: Rotación automática (máximo 10MB por archivo, 3 archivos de histórico) para prevenir consumo excesivo de disco.
  - **Base de datos independiente**: Volumen separado (`db_data_staging`) aislado de producción, ideal para pruebas con datos sintéticos.
  - **Volumen de uploads separado**: Archivos subidos en staging no interfieren con producción (`uploads_staging`).
  - **Configuración equivalente a producción**: Utiliza el mismo `Dockerfile.prod` para detectar problemas antes del despliegue.
  - **Dependencies con condiciones**: Los servicios solo inician cuando sus dependencias están saludables.

## Cómo lanzar

Antes de cualquier entorno, asegúrate de tener `.env` (y `.env.selenium` si usas Selenium) en la raíz del proyecto.

### Comandos básicos

- **Desarrollo**: `docker compose -f docker/docker-compose.dev.yml up -d --build`
- **Producción**: `docker compose -f docker/docker-compose.prod.yml up -d`
- **Producción SSL**: `docker compose -f docker/docker-compose.prod.ssl.yml up -d` (requiere certificados en `docker/letsencrypt` y `public`)
- **Producción webhook**: `docker compose -f docker/docker-compose.prod.webhook.yml up -d --build`
- **Staging (TennisHub)**: `docker compose -f docker/docker-compose.staging.yml up -d --build`

### Comandos específicos de Staging

- **Lanzar sin pruebas de carga**: `docker compose -f docker/docker-compose.staging.yml up -d --build`
- **Lanzar con Locust (pruebas de carga)**: `docker compose -f docker/docker-compose.staging.yml --profile testing up -d --build`
- **Acceder a Locust**: Abre http://localhost:8089 (solo cuando se lanza con `--profile testing`)
- **Verificar healthchecks**: `docker compose -f docker/docker-compose.staging.yml ps`

### Logs y gestión

- **Ver logs**: `docker logs <nombre_contenedor>` (ej: `web_app_container`, `mariadb_container`, `nginx_web_server_container`, `locust_staging`)
- **Ver logs en tiempo real**: `docker logs -f <nombre_contenedor>`
- **Parar entorno**: `docker compose -f <archivo> down`
- **Parar y eliminar volúmenes**: `docker compose -f <archivo> down -v` (⚠️ elimina datos de BD)

### Flujo de trabajo recomendado

1. **Desarrollo local** (`dev`): Implementación de features con hot-reload y Selenium para testing
2. **Staging** (`staging`): Validación, QA, y pruebas de rendimiento con Locust
3. **Producción** (`prod/ssl/webhook`): Despliegue final validado
