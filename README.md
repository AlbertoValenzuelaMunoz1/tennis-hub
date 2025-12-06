<div style="text-align: center;">
  <img src="app/static/img/icons/flavicon.png" alt="Tennis Ball" width="96">
</div>

# Tennis Hub

Fork verticalizado de UVLHub centrado en datasets de tenis. Solo se listan las diferencias relevantes frente al proyecto base; el manual de instalacion y el resto de la documentacion siguen en [docs.uvlhub.io](https://docs.uvlhub.io/).

## Calidad (SonarCloud)

<div align="center">

<table>
  <tr>
    <th style="text-align:center;">Rama main</th>
  </tr>
  <tr>
    <td>
      <a href="https://sonarcloud.io/project/overview?id=egc_tennis-hub">
        <img src="https://img.shields.io/sonar/alert_status/egc_tennis-hub?server=https%3A%2F%2Fsonarcloud.io&label=quality%20gate&style=for-the-badge" alt="Quality Gate main">
      </a>
      <a href="https://sonarcloud.io/project/overview?id=egc_tennis-hub">
        <img src="https://img.shields.io/sonar/coverage/egc_tennis-hub?server=https%3A%2F%2Fsonarcloud.io&style=for-the-badge" alt="Coverage main">
      </a>
      <a href="https://sonarcloud.io/project/overview?id=egc_tennis-hub">
        <img src="https://img.shields.io/sonar/bugs/egc_tennis-hub?server=https%3A%2F%2Fsonarcloud.io&style=for-the-badge" alt="Bugs main">
      </a>
      <a href="https://sonarcloud.io/project/overview?id=egc_tennis-hub">
        <img src="https://img.shields.io/sonar/vulnerabilities/egc_tennis-hub?server=https%3A%2F%2Fsonarcloud.io&style=for-the-badge" alt="Vulnerabilities main">
      </a>
      <a href="https://sonarcloud.io/project/overview?id=egc_tennis-hub">
        <img src="https://img.shields.io/sonar/code_smells/egc_tennis-hub?server=https%3A%2F%2Fsonarcloud.io&style=for-the-badge" alt="Code smells main">
      </a>
      <a href="https://sonarcloud.io/project/overview?id=egc_tennis-hub">
        <img src="https://img.shields.io/sonar/security_hotspots/egc_tennis-hub?server=https%3A%2F%2Fsonarcloud.io&style=for-the-badge" alt="Security hotspots main">
      </a>
      <a href="https://sonarcloud.io/project/overview?id=egc_tennis-hub">
        <img src="https://img.shields.io/sonar/duplicated_lines_density/egc_tennis-hub?server=https%3A%2F%2Fsonarcloud.io&label=duplication&style=for-the-badge" alt="Duplication main">
      </a>
    </td>
  </tr>
</table>

<table>
  <tr>
    <th style="text-align:center;">Rama trunk</th>
  </tr>
  <tr>
    <td>
      <a href="https://sonarcloud.io/project/overview?id=egc_tennis-hub-trunk">
        <img src="https://img.shields.io/sonar/alert_status/egc_tennis-hub-trunk?server=https%3A%2F%2Fsonarcloud.io&label=quality%20gate&style=for-the-badge" alt="Quality Gate trunk">
      </a>
      <a href="https://sonarcloud.io/project/overview?id=egc_tennis-hub-trunk">
        <img src="https://img.shields.io/sonar/coverage/egc_tennis-hub-trunk?server=https%3A%2F%2Fsonarcloud.io&style=for-the-badge" alt="Coverage trunk">
      </a>
      <a href="https://sonarcloud.io/project/overview?id=egc_tennis-hub-trunk">
        <img src="https://img.shields.io/sonar/bugs/egc_tennis-hub-trunk?server=https%3A%2F%2Fsonarcloud.io&style=for-the-badge" alt="Bugs trunk">
      </a>
      <a href="https://sonarcloud.io/project/overview?id=egc_tennis-hub-trunk">
        <img src="https://img.shields.io/sonar/vulnerabilities/egc_tennis-hub-trunk?server=https%3A%2F%2Fsonarcloud.io&style=for-the-badge" alt="Vulnerabilities trunk">
      </a>
      <a href="https://sonarcloud.io/project/overview?id=egc_tennis-hub-trunk">
        <img src="https://img.shields.io/sonar/code_smells/egc_tennis-hub-trunk?server=https%3A%2F%2Fsonarcloud.io&style=for-the-badge" alt="Code smells trunk">
      </a>
      <a href="https://sonarcloud.io/project/overview?id=egc_tennis-hub-trunk">
        <img src="https://img.shields.io/sonar/security_hotspots/egc_tennis-hub-trunk?server=https%3A%2F%2Fsonarcloud.io&style=for-the-badge" alt="Security hotspots trunk">
      </a>
      <a href="https://sonarcloud.io/project/overview?id=egc_tennis-hub-trunk">
        <img src="https://img.shields.io/sonar/duplicated_lines_density/egc_tennis-hub-trunk?server=https%3A%2F%2Fsonarcloud.io&label=duplication&style=for-the-badge" alt="Duplication trunk">
      </a>
    </td>
  </tr>
</table>

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
