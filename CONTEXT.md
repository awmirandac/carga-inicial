# Configuración del entorno local

Cómo dejar andando la generación de catálogos de **NI** en tu máquina, sin Colab.

---

## Qué cambió respecto a Colab

La versión de GT (los scripts en la raíz del repo) corría en Google Colab: montaba Drive y leía CSVs exportados a mano, con la fecha en el nombre del archivo.

```python
# core_cabecera_master_sales.py — como era antes
from google.colab import drive
drive.mount('/content/drive')
FOLDER_CARGA_23_03 = "/content/drive/MyDrive/Test_cargas_iniciales/Pruebas-DEV/23-03-2026/"
df_products_master = pd.read_csv(FOLDER_CARGA_23_03 + "Item_Master_23_03_26.csv")
```

La versión de NI (`NI/`) corre en local y lee el Google Sheet directo por API:

```python
# NI/ni_core_cabecera_master_sales.py — como es ahora
SHEET_ID = "1a-CEDonuVejvxHig8QCn-1hGXN2GJGdYJGHhr0R-Mi4"
spreadsheet = conectar().open_by_key(SHEET_ID)
df_products_master = leer_hoja(HOJA_EQUIPOS)
```

| | Antes (Colab) | Ahora (local) |
|---|---|---|
| Origen de datos | CSVs exportados a mano a Drive | El Google Sheet, leído por API |
| Actualizar datos | Re-exportar el CSV y volver a subirlo | Editar el Sheet y volver a correr |
| Autenticación | `auth.authenticate_user()` con tu cuenta | Cuenta de servicio (archivo JSON) |
| Dependencias | Ya venían en el runtime | `.venv` + `requirements.txt` |
| Salida | Archivo en el runtime, había que descargarlo | Archivo en el repo |

El script **sigue funcionando en Colab**. La función `conectar()` prueba primero el import de `google.colab` y, si falla, cae a la cuenta de servicio local. No hay que tocar nada para cambiar de entorno.

---

## Requisitos

- Python 3.12 (probado con 3.12.3)
- Acceso de lectura al Sheet **Matrices(AVATAR)**
- El archivo de credenciales de la cuenta de servicio (ver más abajo)

---

## Instalación

Desde la raíz del repo:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

`requirements.txt` tiene las versiones fijadas. Las que importan son `gspread` (cliente de Google Sheets), `google-auth` (autenticación) y `pandas`.

---

## Credenciales

La cuenta de servicio es un usuario de Google que no es una persona: tiene su propio mail y su propia llave. El script la usa para leer el Sheet sin pedirte login cada vez.

**1. Conseguir el archivo JSON.** Pedíselo a quien administra el proyecto de Google Cloud. Es un archivo con esta forma:

```json
{
  "type": "service_account",
  "project_id": "lithe-augury-471203-s6",
  "client_email": "carga-inicial-ni@lithe-augury-471203-s6.iam.gserviceaccount.com",
  "private_key": "-----BEGIN PRIVATE KEY-----\n..."
}
```

**2. Dejarlo en la ruta que el script espera:**

```bash
mkdir -p ~/.config/gspread
cp /ruta/donde/lo/bajaste/service_account.json ~/.config/gspread/service_account.json
chmod 600 ~/.config/gspread/service_account.json
```

La ruta está fija en el script y no se cambia por archivo de configuración:

```python
RUTA_CREDENCIALES = os.path.expanduser("~/.config/gspread/service_account.json")
```

**3. Compartir el Sheet con la cuenta de servicio.** Este es el paso que más se olvida. Abrí el Sheet, tocá *Compartir*, y agregá el `client_email` del JSON con permiso de **Lector**. Si no lo hacés, la autenticación funciona pero el Sheet devuelve error de permisos.

> El `private_key` es una credencial real: no lo pegues en Slack ni lo subas al repo. El `.gitignore` ya bloquea todos los `.json` justamente por esto.

---

## Cómo correr

Los dos scripts de NI dependen del cabecera, que es el que carga los datos. **No se importan entre sí**: comparten variables globales, así que hay que ejecutarlos juntos.

**Desde la terminal** (recomendado: cada corrida arranca limpia)

```bash
# Catálogo master -> NI-cargaX-master.xml
cat NI/ni_core_cabecera_master_sales.py NI/ni_core_master_sales.py | .venv/bin/python -

# Catálogo de ventas -> NI-cargaX-sales.xml
cat NI/ni_core_cabecera_master_sales.py NI/ni_core_category_sales.py | .venv/bin/python -
```

Corré siempre desde la raíz del repo: los scripts escriben el XML en el directorio actual.

**Desde VSCode**, con las celdas `# %%`: ejecutá primero todas las del cabecera y después las del master o el category, **en el mismo kernel**.

> Ojo con esto: si editás el Sheet y solo volvés a correr las celdas del master, el script reusa los dataframes viejos que quedaron en memoria y no falla — genera el XML con datos desactualizados. Después de tocar el Sheet, volvé a correr el cabecera o reiniciá el kernel.

---

## Qué no se versiona

El `.gitignore` deja afuera:

```
.venv/          # entorno virtual
__pycache__/    # cache de Python
*.json          # credenciales — nunca versionar
*.xml           # XMLs generados, se rehacen corriendo el script
```

---

## Los datos

Todo sale de un solo Sheet, **Matrices(AVATAR)**, con cuatro pestañas:

| Pestaña | Contenido |
|---|---|
| `PRE-POS-ACC` | Equipos prepago, postpago y accesorios |
| `PLANES-POSTPAGO` | Planes y plan fijo |
| `RELATIONS` | Relación teléfono ↔ plan |
| `CATEGORY_SALES` | Árbol de categorías del catálogo de ventas |

No hay caché en disco: cada corrida trae lo último guardado en el Sheet.

Si alguien **renombra** una pestaña, `leer_hoja` cae a un respaldo por posición y avisa por consola con `AVISO:`. Vale la pena mirar esa línea, porque si además cambió el orden de las pestañas puede estar leyendo la equivocada sin dar error.

---

## Si algo falla

| Error | Qué pasó |
|---|---|
| `FileNotFoundError: No se encontraron las credenciales en ...` | Falta el JSON en `~/.config/gspread/` |
| `gspread.exceptions.APIError: 403` | El Sheet no está compartido con el `client_email` |
| `ModuleNotFoundError: No module named 'gspread'` | Estás usando el Python del sistema; usá `.venv/bin/python` |
| `NameError: name 'df_products' is not defined` | Corriste el master sin el cabecera |
