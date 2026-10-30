# Sistema de Gestión de Usuarios con Tkinter y SQLite3

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/Tkinter-GUI-0088CC?style=for-the-badge" alt="Tkinter GUI" />
  <img src="https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
</div>

Aplicación desktop para gestionar usuarios mediante una interfaz gráfica desarrollada con Python, Tkinter y SQLite3.

## ✨ Características

- Registro de usuarios con datos personales
- Edición y eliminación de registros
- Búsqueda por nombre
- Visualización en tabla dinámica
- Gestión de imagen y archivo adjunto por usuario
- Conexión y desconexión de la base de datos
- Conteo total de usuarios registrados
- Diseño visual moderno con temática morada

## 📁 Estructura del proyecto

```text
Sistema-de-Gestion-de-Usuarios-Tkinter-Sqlite3/
├── README.md
├── SISTEMA DE GESTION USUARIOS/
│   ├── keiner_gestion.py
│   ├── k_galactica.png
│   ├── logo_caribe_tkinter.ico
│   └── adjuntos/                  # archivos e imágenes adjuntados por el usuario
└── keiner.db                      # base de datos SQLite generada al ejecutar la app
```

## 🧰 Requisitos

- Python 3.9 o superior
- Tkinter (incluido en la mayoría de instalaciones de Python)
- SQLite3
- Pillow (opcional, recomendado para mejor manejo de imágenes GIF y JPG)

## ⚙️ Instalación

1. Clona el repositorio:

```bash
git clone https://github.com/keinerrxjas/Sistema-de-Gestion-de-Usuarios-Tkinter-Sqlite3.git
cd Sistema-de-Gestion-de-Usuarios-Tkinter-Sqlite3
```

2. Instala la dependencia opcional de imágenes:

```bash
pip install pillow
```

## ▶️ Ejecución

Desde la raíz del proyecto:

```bash
python "SISTEMA DE GESTION USUARIOS/keiner_gestion.py"
```

O bien, cambia al directorio de la aplicación y ejecuta:

```bash
cd "SISTEMA DE GESTION USUARIOS"
python keiner_gestion.py
```

## 🖥️ Funcionalidades principales

- Formulario para ingresar:
  - nombre
  - apellido
  - dirección
  - ciudad
  - código postal
  - género
  - estado activo/inactivo
  - tipo de usuario
  - imagen
  - archivo adjunto

- Acciones disponibles:
  - Insertar
  - Actualizar
  - Eliminar
  - Limpiar formulario
  - Buscar por nombre
  - Mostrar todos los usuarios

- La aplicación genera automáticamente la base de datos `keiner.db` al conectarse.

## 🗄️ Base de datos

La aplicación usa SQLite con una tabla llamada `usuarios`, donde se almacenan los datos del registro junto con la ruta de la imagen y archivo adjunto.

## 🔒 Nota

El proyecto incluye imágenes y recursos visuales dentro de la carpeta `SISTEMA DE GESTION USUARIOS`, por lo que es recomendable ejecutar la aplicación desde ese directorio o mantener la estructura original intacta para que las rutas de recursos funcionen correctamente.

## 👨‍💻 Autor

Desarrollado por Keiner.

---

Si quieres, también puedo dejarte una versión todavía más profesional con:
- banner tipo portfolio,
- captura de pantalla simulada,
- sección de demo,
- badges personalizados,
- y un estilo más premium para GitHub.
