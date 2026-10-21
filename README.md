# 📒 Agenda de Contactos (Flask + MySQL)

CRUD de contactos con **Python (Flask), HTML, CSS y MySQL**.
La base de datos `agenda_db` y la tabla `contactos` se crean automáticamente al iniciar la app.

## Requisitos
- Python 3.9+
- MySQL (por ejemplo, el de XAMPP) iniciado

## Instalación (Windows)
```bash
git clone https://github.com/TU_USUARIO/agenda-flask.git
cd agenda-flask
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Abre http://127.0.0.1:5000

## Configuración
Por defecto usa `root` sin contraseña (XAMPP). Para cambiarlo, define variables de entorno
antes de ejecutar: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `SECRET_KEY`.

En PowerShell:
```powershell
$env:DB_PASSWORD = "mi_clave"
python app.py
```

## Estructura
```
agenda-flask/
├── app.py            # rutas + creación de la BD
├── templates/        # base.html, index.html, form.html
├── static/css/styles.css
└── requirements.txt
```

## Seguridad
- Consultas parametrizadas (contra inyección SQL)
- Plantillas Jinja2 con escape automático (contra XSS)
- Credenciales por variables de entorno, no en el código
