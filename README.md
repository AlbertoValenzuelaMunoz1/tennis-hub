<div style="text-align: center;">
  <img src="app/static/img/icons/flavicon.png" alt="Tennis Ball" width="96">
</div>

# Tennis Hub

Fork verticalizado de UVLHub centrado en datasets de tenis. Solo se listan las diferencias relevantes frente al proyecto base; el manual de instalacion y el resto de la documentacion siguen en [docs.uvlhub.io](https://docs.uvlhub.io/).

## Calidad (SonarCloud)

<div align="center">

<strong>Rama main</strong>  
<a href="https://sonarcloud.io/project/overview?id=egc_tennis-hub">
  <img src="https://sonarcloud.io/api/project_badges/measure?project=egc_tennis-hub&metric=alert_status" alt="Quality Gate main" />
</a>
<a href="https://sonarcloud.io/project/overview?id=egc_tennis-hub">
  <img src="https://sonarcloud.io/api/project_badges/measure?project=egc_tennis-hub&metric=coverage" alt="Coverage main" />
</a>
<a href="https://sonarcloud.io/project/overview?id=egc_tennis-hub">
  <img src="https://sonarcloud.io/api/project_badges/measure?project=egc_tennis-hub&metric=bugs" alt="Bugs main" />
</a>
<a href="https://sonarcloud.io/project/overview?id=egc_tennis-hub">
  <img src="https://sonarcloud.io/api/project_badges/measure?project=egc_tennis-hub&metric=vulnerabilities" alt="Vulnerabilities main" />
</a>

<strong>Rama trunk</strong>  
<a href="https://sonarcloud.io/project/overview?id=egc_tennis-hub-trunk">
  <img src="https://sonarcloud.io/api/project_badges/measure?project=egc_tennis-hub-trunk&metric=alert_status" alt="Quality Gate trunk" />
</a>
<a href="https://sonarcloud.io/project/overview?id=egc_tennis-hub-trunk">
  <img src="https://sonarcloud.io/api/project_badges/measure?project=egc_tennis-hub-trunk&metric=coverage" alt="Coverage trunk" />
</a>
<a href="https://sonarcloud.io/project/overview?id=egc_tennis-hub-trunk">
  <img src="https://sonarcloud.io/api/project_badges/measure?project=egc_tennis-hub-trunk&metric=bugs" alt="Bugs trunk" />
</a>
<a href="https://sonarcloud.io/project/overview?id=egc_tennis-hub-trunk">
  <img src="https://sonarcloud.io/api/project_badges/measure?project=egc_tennis-hub-trunk&metric=vulnerabilities" alt="Vulnerabilities trunk" />
</a>

</div>

## Diferencias clave frente a UVLHub
- Tematizacion tenis + nuevos textos/identidad.
- Doble factor de autenticacion (2FA) usando `pyotp` y generacion de QR con `qrcode[pil]`.
- Carrito de descargas
- Comentarios por dataset
- Contador de descargas
- Subir dataset desde github o archivo zip
- Ranking de datasets en tendencia.
- Integracion con FakeNODO/Zenodo para publicaciones de datasets.
- Workflows: analisis SonarQube separados por ramas (`main` produccion, `trunk` desarrollo).
- Despliegue en Render diferenciado: `main` apunta a produccion y `trunk` a desarrollo/staging.

## Entorno de pruebas local
- Se incluye `.env.local_testing.example` para lanzar la suite: copia y renombra antes de probar.
  ```bash
  cp .env.local_testing.example .env
  ```
- Configura `WORKING_DIR`, credenciales de MariaDB y SMTP (para los OTP) en ese `.env`.

## Documentacion
Todo el manual de instalacion, despliegue y guias de uso se mantiene en [docs.uvlhub.io](https://docs.uvlhub.io/).
