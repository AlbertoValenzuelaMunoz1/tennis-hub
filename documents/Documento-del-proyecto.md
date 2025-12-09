 ## Indicadores del proyecto

(_debe dejar enlaces a evidencias que permitan de una forma sencilla analizar estos indicadores, con gráficas y/o con enlaces_)

Miembro del equipo  | Horas | Commits | LoC | Test | Issues | Work Item| Dificultad
------------- | ------------- | ------------- | ------------- | ------------- | ------------- |  ------------- |  ------------- | 
[Valenzuela Muñoz,Alberto](https://github.com/AlbertoValenzuelaMunoz1) | 50 | Commit | 711 | ZZ | Implementación de workflows de Sonar Qube | Comentarios de Dataset, Fakenodo| H/M/L |
[Rivas Becerra, Mario](https://github.com/marrivbec) | 50 | XX | YY | ZZ | II | Implementación de la vista "Trending Datasets" | H/M/L |
[Roldán Pérez, Antonio](https://github.com/AntonioRolpe11) | 50 | XX | YY | ZZ | II | Descargar nuestro propio dataset | H/M/L |
[Ramírez Morales, Juan](https://github.com/Juanramire) | 50 | XX | YY | ZZ | II | 2FA, Contador de descargas | H/M/L |
[Ferrer Álvarez, Ángel Manuel](https://github.com/angelmanuelferrer) | HH | XX | YY | ZZ | II | Subir desde Github/Zip | H/M/L |¡
[Ruiz Fernández, Javier](https://github.com/javruifer1) | 50 | XX | YY | ZZ | II | Implementar nuevos tipos de dataset | H/M/L |
**TOTAL** | 300  | tXX | tYY | tZZ | tII | Descripción breve | H (X)/M(Y)/L(Z) |

La tabla contiene la información de cada miembro del proyecto y el total de la siguiente forma: 
  * Horas: número de horas empleadas en el proyecto.
  * Commits: commits hechos por miembros del equipo.
  * LoC (líneas de código): líneas producidas por el equipo y no las que ya existían o las que se producen al incluir código de terceros.
  * Test: test realizados por el equipo.
  * Issues: issues gestionadas dentro del proyecto y que hayan sido gestionadas por el equipo.
  * Work Item: principal WI del que se ha hecho cargo el miembro del proyecto.
  * Dificultad: señalar el grado de dificultad en cada caso. Además, en los totales, poner cuántos se han hecho de cada grado de dificultad entre paréntesis. 


## Resumen ejecutivo
El proyecto desarrollado, denominado Tennis-Hub, no nace desde cero, sino que constituye una refactorización del sistema de código abierto conocido como UVLHUB. El objetivo principal de esta transformación ha sido migrar de un repositorio de datos genérico a una plataforma especializada en la gestión, almacenamiento y distribución de datasets relacionados exclusivamente con el mundo del tenis. Esto ha implicado no solo cambios estéticos, sino una reestructuración de la lógica de negocio para soportar nuevas funcionalidades que enriquecen la interacción del usuario y aumentan la robustez de la seguridad del entorno.

1. Experiencia de Usuario (UX)
El primer nivel de intervención se centró en la "Personalización y Refactorización Visual". El sistema original carecía de una identidad temática definida. Para Tennis-Hub, se ha implementado una nueva guía de estilo que alinea la paleta de colores, la tipografía y la disposición de los elementos (layout) con la estética deportiva del tenis.

2. Módulo de Transacciones y Gestión de Recursos (El Carrito)
Una de las innovaciones funcionales más destacadas respecto al proyecto base es la implementación del Sistema de Carrito de Datasets. Inspirado en los patrones de diseño del comercio electrónico (e-commerce). En lugar de obligar al usuario a realizar descargas unitarias y repetitivas, el sistema permite ahora la selección múltiple de recursos.

Esto se gestiona mediante el almacenamiento en sesión (session storage) de las referencias a los datasets seleccionados. El usuario puede navegar por distintas categorías, añadir archivos a su "carrito" virtual y, finalmente, proceder a una gestión unificada. Esto culmina en el módulo de Gestión de Descargas, que ha sido optimizado para manejar la entrega eficiente de estos archivos, permitiendo al investigador o aficionado obtener todo el material necesario en un solo flujo de trabajo, optimizando el tiempo y el ancho de banda.

3. Métricas de Popularidad
Para transformar un repositorio estático en una comunidad dinámica, se han integrado Módulos de Interacción. La característica central aquí es el sistema de comentarios. Se ha desarrollado un sistema CRUD (Create, Read, Update, Delete) que permite a los usuarios registrados iniciar hilos de discusión en cada dataset. Esto añade una capa de valor cualitativo a los datos: los usuarios pueden advertir sobre erratas en los archivos, sugerir mejoras o compartir análisis derivados.

Paralelamente, se ha introducido un motor de análisis de tendencias. El sistema incorpora contadores internos que registran eventos de visualización y descarga en tiempo real. Estos datos alimentan la sección de "Datasets de Moda" (Trending), un algoritmo de ordenamiento que destaca en la página principal aquellos recursos que están recibiendo mayor atención por parte de la comunidad. Esto no solo mejora la descubribilidad del contenido, sino que ofrece a los administradores una visión clara de qué tipo de información es la más demandada.

4. Seguridad Avanzada: Doble Factor de Autenticación (2FA)
Dada la importancia de proteger las cuentas de usuario y la integridad de los datos subidos, se ha elevado la seguridad mediante la integración de Doble Factor de Autenticación (2FA).

El flujo implementado requiere que, tras la validación tradicional de usuario y contraseña, el sistema genere un token. El acceso al sistema permanece bloqueado en una vista intermedia hasta que el usuario introduce el código correcto. Esta implementación asegura que, incluso si una contraseña es filtrada, el atacante no podrá acceder a la cuenta sin tener control simultáneo sobre el correo electrónico del propietario.

5. Infraestructura y Despliegue en la Nube
Finalmente, la arquitectura de despliegue ha sido modernizada utilizando Render, una plataforma en la nube (PaaS). Para el ciclo de vida del desarrollo de software, se han establecido dos entornos completamente diferenciados:

* Entorno de Desarrollo: Un espacio volátil donde se despliegan las nuevas funcionalidades (features) para su integración y revisión inicial.

* Entorno de Pruebas (Staging): Un espejo del entorno de producción donde se realizan las validaciones finales, pruebas de carga, además de la implementación de nuevas funcionalidades.

Esta separación de entornos, cada uno con su propia instancia de base de datos, permite al equipo validar cambios, probar migraciones y ejecutar tests de regresión sin poner en riesgo la estabilidad del sistema ni la integridad de los datos visibles para los usuarios finales.

## Descripción del sistema
La arquitectura de Tennis-Hub sigue el patrón de diseño Modelo-Vista-Controlador (MVC), implementado a través del framework Flask. Esta decisión arquitectónica permite desacoplar la lógica de negocio de la interfaz de usuario, facilitando la mantenibilidad y escalabilidad del sistema.

* Capa de Presentación (Vista/Templates): Desarrollada en HTML5 y CSS3, utiliza el motor de plantillas Jinja2 integrado en Flask. Esta capa es responsable de renderizar la información enviada por el servidor y capturar las interacciones del usuario. Se ha diseñado con un enfoque responsive para adaptarse a distintos dispositivos.

* Capa de Lógica de Negocio (Controlador/Rutas): Gestionada por los controladores de Flask (routes.py o views.py). Aquí residen los algoritmos que procesan las peticiones HTTP (GET, POST), gestionan la lógica del carrito de compras, validan el 2FA y calculan las tendencias de los datasets.

* Capa de Datos (Modelo): Se utiliza SQLAlchemy como ORM (Object-Relational Mapper). Esto permite interactuar con la base de datos mediante clases de Python en lugar de escribir SQL crudo, abstrayendo la complejidad de las consultas. Los modelos principales incluyen entidades como User, Dataset, Comment y Order."

El sistema interactúa con subsistemas críticos:
* Sistema de Almacenamiento: Gestión de archivos estáticos donde se alojan los datasets físicos.
* Render (PaaS): Plataforma que orquesta el despliegue, gestionando el servidor de aplicaciones (Gunicorn/uWSGI) y la conexión a la base de datos en la nube.

Desde la perspectiva funcional, el sistema se divide en módulos interconectados:

* Módulo de Gestión de Usuarios y Seguridad (Auth) "Este módulo administra el ciclo de vida de las cuentas. La mejora más significativa es la implementación del Doble Factor de Autenticación (2FA). Tras el inicio de sesión estándar (usuario/contraseña), el sistema genera un token temporal enviado al correo del usuario, bloqueando el acceso hasta su validación. Esto mitiga riesgos de suplantación de identidad."

* Módulo de Datasets y Tendencias Es el núcleo de Tennis-Hub. Los usuarios pueden subir archivos que son indexados por el sistema. Se ha incorporado un algoritmo de popularidad que alimenta la sección 'Datasets de Moda'. Este subsistema utiliza contadores internos que registran visualizaciones y descargas, ordenando dinámicamente los recursos en la página principal para destacar el contenido más relevante.

* Módulo de Interacción Social Para fomentar la comunidad, se ha desarrollado un sistema de comentarios. Cada dataset cuenta con un hilo de discusión persistente donde los usuarios pueden aportar feedback, correcciones o análisis sobre los datos, convirtiendo el repositorio estático en un espacio dinámico de conocimiento.

* Módulo Transaccional (El Carrito) Inspirado en e-commerce, se introduce el concepto de 'Carrito de Datasets'. Funcionalmente, permite a los usuarios seleccionar múltiples archivos de interés mientras navegan, agregándolos a una lista temporal. Posteriormente, el usuario puede proceder a la 'descarga unificada' o gestión en bloque de estos recursos, mejorando la usabilidad frente a la descarga uno a uno.

El proyecto parte de la base de UVLHUB, pero ha sufrido una transformación sustancial. A continuación, se enumeran explícitamente los cambios desarrollados e integrados en la versión final de Tennis-Hub:

* Refactorización de Marca e Interfaz:
  * Modificación completa de la paleta de colores, logotipos y tipografías para alinearse con la temática de tenis.
  * Adaptación de los textos y terminología de la interfaz (traducción y localización al dominio deportivo).

* Implementación de Seguridad Avanzada (2FA):
  * Desarrollo de lógica backend para la generación de tokens OTP (One-Time Passwords).
  * Creación de nuevas vistas y formularios para la introducción del código de verificación.
  * Integración con servidor de correo para el envío de alertas.

* Sistema de Carrito de Compras (Dataset Cart):
  * Creación de estructuras de datos de sesión para almacenar selecciones temporales.
  * Desarrollo de la interfaz flotante o página dedicada para visualizar los items seleccionados.
  * Implementación de la lógica de descarga masiva o checkout.

* Métricas y 'Trending Dataset':
  * Modificación del modelo de base de datos Dataset para incluir campos de contadores (view_count, download_count).
  * Creación de la lógica de ordenamiento para filtrar y mostrar los 'Datasets de Moda' en la landing page.

* Feedback de Usuario:
  * Desarrollo del sistema para comentarios asociados a cada dataset.
  * Validación de permisos para asegurar que solo usuarios registrados puedan comentar.

## Visión global del proceso de desarrollo 
El proceso para desarrollar Tennis-Hub fue más que solo escribir código. Se trató de meterse de lleno en una cadena completa, súper profesionalizada, de DevOps y control de calidad. Esto aseguraría que cada nueva función se validará antes de que los usuarios finales la vieran. Es esta mirada general del asunto lo que hizo que el sistema, a pesar de venir de un proyecto viejo, se convirtiera en una plataforma robusta, moderna y que se puede mantener. Cada pequeña elección, desde cómo organizar el repositorio hasta automatizar las implementaciones, siempre tuvo el objetivo de mejorar la estabilidad, legibilidad y facilidad de actualización del proyecto.

1. Flujo de trabajo usando ramas y CI:
El equipo eligió un flujo de trabajo inspirado en el desarrollo basado en trunk, usando ramificaciones cortas y super controladas. Cada cambio parte de la rama principal, trunk, y se trabaja en una rama separada.
Una vez que la funcionalidad está lista se integra de vuelta en trunk. Allí, diversas herramientas automatizadas —incluidas SonarCloud, Codacy, y las pruebas de integración— comprueban la calidad estática del código, buscando posibles fallos lógicos, vulnerabilidades de seguridad y duplicación, ademas verifican el estilo del proyecto.

Esta estrategia disminuye mucho la chance de meter problemillas críticos, porque las ramas no amontonan montones de cambios grandes y duran muy poco. Encima, trabajando poco a poco, las revisiones de código son más rápidas y ayudan a enfocar mejor la consistencia de la arquitectura.

La revisión del código no es visto como un simple tramite, sino como un paso esencial para asegurar la coherencia, pillar problemas antes, y asegurar que el sistema siga un estilo común, aunque participe más gente en su desarrollo.

2. Automatización de pruebas y validación antes del despliegue:
Las pruebas automáticas es ahora, un pilar fundamental en el flujo de trabajo. Se definieron tres niveles, ademas complementarios:

  * Pruebas unitarias revisan la lógica de los métodos modelos y controladores aisladamente. Aseguran, eso sí, que la función base se mantenga sin cambios pese a futuras modificaciones.

  * Pruebas funcionales con Selenium, simulan acciones reales del usuario en el navegador, para revisar formularios, rutas protegidas, navegación, autenticación y todas interacciones complejas. Gracias a estas pruebas, pudimos validar el comportamiento completo del sistema desde la visión del usuario final.

  * Pruebas de carga con Locust. Permiten medir el comportamiento del sistema bajo escenarios de mucho tráfico, simulando usuarios simultáneos descargando datasets, navegando por páginas, o accediendo a funciones críticas como el login. Este tipo de prueba resultó, digamos, especialmente valiosa para encontrar problemas y optimizar consultas o endpoints con mucha concurrencia.

Este conjunto de pruebas hizo posible detectar problemas pronto y ayudó a garantizar la estabilidad de la aplicación antes de implementarla en entornos superiores. Además, ayudo a mantener una calidad constante, incluso con un aumento significativo de las funciones.

Ciclo de vida del proyecto administrado:

  * El tablero Kanban, junto a las issues y los commits, fueron artefáctos esenciales pa' documentar el progreso del proyecto. El equipo mantuvo una disciplina rigurosa al escribir issues y commits, por eso, cualquier miembro podía entender la evolución del desarrollo, en segundos.

Esta clara organización del flujo nos ayudó a detectar bloqueos, asignar mejor las tareas, y garantizar el registro correcto de cada paso. Cuando un cambio superaba las revisiones, se movía a la columna IN REVIEW, y después, a DONE.

Gracias a este enfoque, todo el equipo estaba al tanto del estado del proyecto al instante, ademas la trazabilidad se mantuvo por meses, simplificando auditorías, refactorizaciones y futuras mejoras.

4. Diferenciación de entornos: Staging, Producción y Desarrollo:

Otro pilar important fue la distinta separación entre entornos:

  * Desarrollo: despliegue automático de la rama trunk, esto se uso para validar la integración de cambios recientes. Le da la oportunidad al equipo de ver el resultado de cada merge, inmediatamente.
  * Staging, es como un reflejo de producción, ahi se hacen las pruebas finales, en especial, las de carga y como se relacionan los módulos. Allí, se simulan situaciones reales, antes de aprobar una versión.
  * Producción: es el lugar donde se lanza la rama principal, solamente cuando se hace una versión estable nueva. Solo se publica cuando todas las revisiones se han superado.

Esta táctica, reduce peligros y deja verificar cualquier cambio en lugares seguros antes de afectar a los usuarios de verdad. La plataforma Render ayudo esta coordinación, gestionando los servicios y las bases de datos relacionadas, eso, dejo un despliegue repetible, automático y muy controlado.

5. Un proceso guiado por aprendizaje en equipo:
Más alla del resultado final, el proyecto fue un completo entrenamiento, en la práctica profesional del desarrollo como; planificación, control de versiones, trabajo en grupo, depuración, documentación, automatización, y lanzamiento.

El equipo se esforzó no solo para crear una app que funcionara, si no para hacerla de la manera más correcta, empleando buenas practicas, herramientas modernas y una metodología ya madura.

Ese método ayudó a ganar expertise en cosas fundamentales, por ejemplo:
  * Atajar fallos rápido usando integración continua,
  * Emplear contenedores pa' uniformar ambientes,
  * Código uniforme gracias a linters y reglas automaticas,
  * Aplicar métricas de calidad con la mira puesta en mejorar siempre,
  * Una documentación clara pensada pa' colaborar más adelante.

El producto final es un sistema estable, expandible, todo ordenado; podemos seguir agregando funciones sin afectar la estructura central.
Esta perspectiva del proceso revela como cada desicion, desde usar Docker hasta adoptar Conventional Commits, conformó un flujo ideado pa' obtener calidad, seguimiento y eficacia, plantando así una base fuerte donde seguir construyendo.

## Ejercicio de propuesta de cambio

### 1 Creación de la tarea en el tablero del proyecto
El primer paso consiste en registrar la tarea en el tablero de gestión del proyecto. Para ello, se crea una issue que describa de manera clara y concisa el objetivo del cambio: ya sea implementar una nueva funcionalidad, corregir un error existente o realizar una mejora en el sistema. Una vez generada, la tarea se ubica inicialmente en la columna TO DO, donde se encuentran todos los elementos pendientes de abordar. Esta fase permite que el equipo mantenga una visión global del trabajo por realizar y que las tareas queden correctamente priorizadas antes de comenzar su desarrollo.

### 2 Creación de la rama correspondiente
Antes de empezar a implementar cualquier cambio en el código, es necesario crear una nueva rama en el repositorio. Esta rama siempre debe originarse desde la rama trunk. El nombre de la rama dependerá del tipo de modificación que se vaya a realizar: “feature-task/nombre-de-la-tarea” para funcionalidades nuevas o ampliaciones, y “bugfix/descripción-del-cambio” para resolver errores. Para crear la rama se ejecutan los siguientes comandos: git checkout trunk y git checkout -b nombre-de-la-rama. Una vez creada la rama, se actualiza el tablero moviendo la issue al estado IN PROGRESS, indicando así al resto del equipo que se ha comenzado a trabajar en dicha tarea.

### 3 Desarrollo de la tarea y subida inicial de cambios
Con la rama creada, se procede al desarrollo de la tarea. Durante esta fase, es recomendable realizar commits periódicos, especialmente si se desea compartir los avances con otros miembros del equip. Para subir los cambios se ejecutan los comandos git add ., git commit -m "mensaje-del-commit" y git push. Es importante respetar el formato de Conventional Commits, lo cual facilita la comprensión del historial y permite automatizar procesos como el versionado semántico. El mensaje del commit deberá seguir la estructura “feat: descripción del cambio” para nuevas funcionalidades o “fix: descripción del cambio” para correcciones. El mensaje debe ser claro, breve y descriptivo.

### 4 Ejecución de pruebas
Una vez completada la implementación, se debe realizar un conjunto de pruebas que validen la calidad y el correcto funcionamiento de los cambios. Entre las pruebas contempladas se incluyen pruebas de interfaz utilizando Selenium, pruebas de carga con Locust y pruebas unitarias. Tras completar las pruebas, , es necesario subir estos cambios a la rama siguiendo los comandos anteriores. Si el commit contiene únicamente pruebas, el prefijo adecuado será “test”, en caso contrario será el descrito en el paso anterior, manteniendo el estándar de Conventional Commits.

### 5 Integración de cambios en la rama trunk
Cuando la tarea ha sido desarrollada y validada con las pruebas correspondientes, llega el momento de incorporar los cambios en la rama trunk del proyecto. El procedimiento consiste en ejecutar git checkout trunk, git merge nombre-de-la-rama y git push. Esto actualiza la rama trunk con el nuevo código. Luego, la tarea se mueve a la columna REVIEW del tablero, indicando que está lista para ser revisada por el equipo. Si los miembros consideran que los cambios son correctos, la tarea pasa a DONE. Si se requieren correcciones, se vuelve al paso 3 para aplicar los cambios necesarios, subirlos de nuevo y repetir el proceso de revisión. Para este paso, el equipo dispondrá del despliegue de la rama trunk en render, cuya finalidad es el desarrollo así como análisis en Sonar Cloud y Codacy del código como ayuda para revisar el código realizado.

### 6 Integración en rama main
Por último, cuando el equipo de desarrollo considera oportuno generar una nueva release, se procede a integrar los cambios de la rama trunk en la rama main y a crear una nueva etiqueta de versión. Para ello, se ejecutan los siguientes comandos en este orden: git checkout main, git merge trunk, git push, git tag -a version, y finalmente git push origin version. La versión asignada debe seguir el esquema de versionado semántico, es decir, el formato MAJOR.MINOR.PATCH. En este sistema, MAJOR se incrementa cuando se realizan cambios que rompen la compatibilidad del proyecto, MINOR se utiliza para añadir nuevas funcionalidades que no afectan la compatibilidad y PATCH se incrementa cuando se realizan correcciones de errores o mejoras menores que no modifican el comportamiento general del sistema.


### Conclusiones y trabajo futuro
Se enunciarán algunas conclusiones y se presentará un apartado sobre las mejoras que se proponen para el futuro (curso siguiente) y que no han sido desarrolladas en el sistema que se entrega