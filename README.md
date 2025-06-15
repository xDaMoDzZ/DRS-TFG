# 💻 System Admin CLI

¡Bienvenido al **System Admin CLI**! Una herramienta minimalista de línea de comandos desarrollada en Python, diseñada para simplificar y unificar la administración de sistemas tanto en **Windows Server** como en **Linux Server**. Olvídate de recordar comandos específicos para cada sistema operativo; con System Admin CLI, tendrás un menú interactivo y elegante para gestionar tus servidores.

# 💻 System Admin GUI
Además, también he desarollado una interfaz más amigable con el usuario, centrándome en las pequeñas empresas (pymes) y en coste de la gestión informática en la que deben invertir. Gracias a ésta interfaz gráfica, estas pequeñas empresas podrán gestionar de forma más sencilla e intuitiva las labores y necesitades principales. **Disponible tanto en Windows como en Linux**.

---

## ✨ Características Principales

- **Administración Unificada:** Controla usuarios y grupos, redes, firewall, procesos y particiones de disco tanto en Windows como en Linux desde una única interfaz.
- **Interfaz de Menú Intuitiva:** Navega fácilmente a través de menús numerados, con la opción `0` para volver atrás o salir.
- **Comandos Nativos:** Desarrollado para ser 100% compatible con los comandos base de Windows y Linux, minimizando la dependencia de librerías externas.
- **Logging Integrado:** Todas las acciones importantes se registran en archivos de log para auditoría y seguimiento.
- **Diseño Minimalista y Atractivo:** Una experiencia de terminal limpia y bien presentada, diseñada para ser agradable a la vista.

---

## 🚀 Empezando

Sigue estos sencillos pasos para poner en marcha el System Admin CLI en tu servidor:

### 1. Clonar el Repositorio

Abre tu terminal y clona el repositorio de GitHub:

```bash
git clone https://github.com/xDaMoDzZ/DRS-TFG.git
cd DRS-TFG
```

### 2. Estructura del Proyecto

Asegúrate de que la estructura de archivos sea la siguiente después de clonar:

```
DRS-TFG/
├── main.py
├── utils/
│   ├── display.py
│   ├── system_info.py
│   └── logger.py
├── modules/
│   ├── __init__.py
│   ├── user/
│   │   └── user_group_management.py
│   ├── network/
│   │   └── network_management.py
│   ├── resource/
│   │   └── resource_monitoring.py
│   ├── disk/
│   │   └── disk_partition_management.py
│   ├── firewall/
│   │   └── firewall_management.py
│   ├── process/
│   │   └── process_management.py
│   ├── services
│   │   └── service_management.py
│   ├── package
│   │   └── package_management.py
│   ├── docker
│   │   └── docker_management.py
│   └── gui
│       └── gui_interface.py
├── config.py
├── README.md
└── LICENSE.md

```

### 3. Ejecutar el Script

Para iniciar la aplicación, ejecuta `main.py`. **¡Importante!** Para la mayoría de las funcionalidades de administración, necesitarás **privilegios de administrador/root**:

#### En Windows

Abre `CMD` o `PowerShell` **como administrador** (clic derecho -> "Ejecutar como administrador") y luego navega a la carpeta del proyecto:

```bash
python main.py
```

#### En Linux 🐧

Puedes ejecutar el script directamente o usar `sudo` para asegurar los permisos:

```bash
python3 main.py
# O si necesitas permisos elevados
sudo python3 main.py
```

---

## 🛠️ Uso

Una vez iniciado, serás recibido por el menú principal. Simplemente introduce el número de la opción que desees y presiona `Enter`.

```
======================================
   Administración de Sistemas (Linux)
======================================

[1] Administración de Usuarios y Grupos
[2] Administración de Redes
[3] Monitorización de Recursos
[4] Gestión de Particiones de Disco
[5] Gestión de Firewall
[6] Gestión de Procesos
[0] Salir
------------------------------
Seleccione una opción:
```

### 📝 Logs

Todas las acciones que modifiquen el sistema o generen información relevante se registrarán automáticamente en el directorio `logs/` dentro de la raíz del proyecto. Los logs se organizan por fecha.

---

> [!Warning] Advertencias y Consideraciones
> 
> - **¡Requiere Privilegios!** Muchas operaciones requieren permisos de administrador/root. Asegúrate de ejecutar el script con los permisos adecuados.
> - **Uso de Comandos Nativos:** El script depende de los comandos de sistema operativo. Asegúrate de que los comandos básicos (como `net user`, `ipconfig`, `tasklist` en Windows; `useradd`, `ip`, `ps`, `ufw` en Linux) estén disponibles en tu `PATH`.
> - **Entornos de Servidor:** Diseñado principalmente para entornos de servidor. Las funcionalidades de monitorización pueden ser más detalladas en Linux debido a la naturaleza de las herramientas disponibles en CLI.
> - **Validación de Entrada:** Aunque se intenta manejar la entrada del usuario, sé cauteloso con los valores que introduces, especialmente en operaciones críticas.

---

## 🤝 Contribuciones

¡Tu ayuda es bienvenida! Si encuentras un bug, tienes una sugerencia de mejora o quieres añadir una nueva funcionalidad, no dudes en abrir un _issue_ o enviar un _Pull Request_.

---
## 📜 Licencia

Este proyecto está bajo la Licencia Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International. Consulta el archivo `LICENSE` para más detalles.
