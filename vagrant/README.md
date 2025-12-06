# Vagrant

Dos configuraciones principales:

- **Despliegue (produccion/staging)**: arranca la app con `gunicorn` en lugar de `flask run`. No instala MariaDB en la VM; usa la base definida en tu `.env` (host externo o servicio gestionado). Ajusta las variables `MARIADB_HOSTNAME`, `MARIADB_PORT`, `MARIADB_DATABASE`, `MARIADB_USER`, `MARIADB_PASSWORD` en la raiz antes de levantar la maquina. Ideal cuando Render u otro entorno ya provee la base.

- **Desarrollo**: arranca con `flask run --reload` (ver `05_run_app.yml`) e instala MariaDB dentro de la VM (`02_install_mariadb.yml` + `03_mariadb_scripts.yml`). Crea las bases `MARIADB_DATABASE` y `MARIADB_TEST_DATABASE` y aplica seeds via `rosemary db:seed -y --reset`. Usa el `.env` de la raiz para configurar credenciales y nombre de bases.

Notas rapidas:
- El `Vagrantfile` carga el `.env` de la raiz y pasa sus variables a los playbooks de Ansible.
- Si quieres usar el modo despliegue (gunicorn + DB externa), omite la provision de MariaDB local o ajusta los playbooks para saltarse `02_install_mariadb.yml` y `03_mariadb_scripts.yml`.
- Para el modo desarrollo basta con `vagrant up`; se provisiona todo (dependencias, MariaDB local, migraciones, seeds) y expone el puerto 5000 de Flask.
