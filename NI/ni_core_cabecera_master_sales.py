# %% Constantes
MASTER_CATALOG_NAME = 'NI-test-claro-master'
SALES_CATALOG_NAME = 'NI-test-claro-sales'

EXTERNAL_LOCATION_HTTP = 'http://tiendaenlinea.claro.com.ni/cdn/'
EXTERNAL_LOCATION_HTTPS = 'https://tiendaenlinea.claro.com.ni/cdn/'

# Moneda del catalogo (tal como figura en la matriz)
CURRENCY = 'NIO'
# Plazo de financiamiento vigente en Nicaragua
PAYMENT_TERM = 18

ATTR_PREFFIXES = ['ATTR_CHARS_', 'ATTR_TECHSPECH_', 'ATTR_CONF_', 'ATTR_DETALLE_', 'CEN_COLOR', 'CEN_STORAGE', 'CEN_MODALITY', 'CATEGORY_CODE', 'attr_conf_modalidad', 'ATTR_TEXTO_CUOTAS']
CEN_PREFFIXES = ['cen_', 'c_cen_esim_support']
DESCRIPCION_PREFFIXES = ['descripcion_']
PLAN_PREFFIXES = ['plan_']
HOGAR_PREFFIXES = ['hogar_']

PRODUCT_OPTION_PLAN = 'planesPostpagoOptions'

# %% Carga de datos (Google Sheet)

import csv
import io
import os

import gspread
import pandas as pd

# Fuente unica: el Google Sheet "Matrices(AVATAR)" y sus 4 pestanas
SHEET_ID = "1a-CEDonuVejvxHig8QCn-1hGXN2GJGdYJGHhr0R-Mi4"

# Credenciales de la cuenta de servicio (solo se usan fuera de Colab)
RUTA_CREDENCIALES = os.path.expanduser("~/.config/gspread/service_account.json")

# (nombre de la pestana, posicion de respaldo si el nombre llegara a cambiar)
HOJA_EQUIPOS    = ('PRE-POS-ACC', 0)        # prepago, pospago y accesorios
HOJA_PLANES     = ('PLANES-POSTPAGO', 1)    # planes y plan fijo
HOJA_RELACIONES = ('RELATIONS', 2)          # relacion telefono-plan
HOJA_CATEGORIAS = ('CATEGORY_SALES', 3)     # arbol de categorias del catalogo de ventas


def conectar():
    """En Colab autentica con la sesion del usuario; en local, con la cuenta de servicio."""
    try:
        from google.auth import default
        from google.colab import auth
        auth.authenticate_user()
        credenciales, _ = default()
        return gspread.authorize(credenciales)
    except ImportError:
        if not os.path.exists(RUTA_CREDENCIALES):
            raise FileNotFoundError(
                f"No se encontraron las credenciales en {RUTA_CREDENCIALES}")
        return gspread.service_account(filename=RUTA_CREDENCIALES)


spreadsheet = conectar().open_by_key(SHEET_ID)
pestanas = {ws.title: ws for ws in spreadsheet.worksheets()}
print("Pestanas encontradas:", list(pestanas))


def leer_hoja(hoja):
    """Devuelve la pestana como dataframe, con el mismo parseo que tenia el CSV exportado."""
    nombre, posicion = hoja
    if nombre in pestanas:
        ws = pestanas[nombre]
    else:
        titulos = list(pestanas)
        if posicion >= len(titulos):
            raise KeyError(f"No se encontro la pestana '{nombre}'. Disponibles: {titulos}")
        ws = pestanas[titulos[posicion]]
        print(f"AVISO: no existe la pestana '{nombre}', se usa '{ws.title}' (posicion {posicion})")

    buffer = io.StringIO()
    csv.writer(buffer).writerows(ws.get_all_values())
    buffer.seek(0)
    return pd.read_csv(buffer)


df_products_master = leer_hoja(HOJA_EQUIPOS)
df_products_master_plan = leer_hoja(HOJA_PLANES)
df_products_master_relations_phone_plan = leer_hoja(HOJA_RELACIONES)
df_sales_categories = leer_hoja(HOJA_CATEGORIAS)
# df_products: df de pre, pos y otros
df_products = df_products_master
# df_products_plan_fijo: df solo de plan fijo
df_products_plan_fijo = df_products_master_plan[df_products_master_plan['ATTR_CONF_TIPOPRODUCTO'] == 'PLANFIJO']
# df_products_options: df solo de planes
df_products_options = df_products_master_plan[df_products_master_plan['ATTR_CONF_TIPOPRODUCTO'] == 'PLAN']

df_products['CEN_COLOR']    = df_products['DEF_COLOR']
df_products['CEN_STORAGE']  = df_products['DEF_CAPACIDAD']
df_products['CEN_MODALITY']  = df_products['ATTR_CONF_TIPOPRODUCTO']

df_products_plan_fijo['CEN_COLOR']    = df_products_plan_fijo['DEF_COLOR']
df_products_plan_fijo['CEN_STORAGE']  = df_products_plan_fijo['DEF_CAPACIDAD']
df_products_plan_fijo['CEN_MODALITY']  = df_products_plan_fijo['ATTR_CONF_TIPOPRODUCTO']

df_products_options['CEN_COLOR']    = df_products_options['DEF_COLOR']
df_products_options['CEN_STORAGE']  = df_products_options['DEF_CAPACIDAD']
df_products_options['CEN_MODALITY']  = df_products_options['ATTR_CONF_TIPOPRODUCTO']

# %% Limpieza de dataframes

dataframes_to_clean = [df_products, df_products_plan_fijo, df_products_options]

for df in dataframes_to_clean:

    if 'DEF_COLOR' in df.columns: df['DEF_COLOR'] = df['DEF_COLOR'].fillna('vacio')
    if 'DEF_CAPACIDAD' in df.columns: df['DEF_CAPACIDAD'] = df['DEF_CAPACIDAD'].fillna('vacio')
    if 'DEF_PANTALLA' in df.columns: df['DEF_PANTALLA'] = df['DEF_PANTALLA'].fillna('vacio')
    if 'FILT_MARCA' in df.columns: df['FILT_MARCA'] = df['FILT_MARCA'].fillna('vacio')
    if 'ATTR_CHARS_MAIN_PILA' in df.columns: df['ATTR_CHARS_MAIN_PILA'] = df['ATTR_CHARS_MAIN_PILA'].fillna('vacio')
    if 'ATTR_TECHSPECH_RESUMEN_TAMANO' in df.columns: df['ATTR_TECHSPECH_RESUMEN_TAMANO'] = df['ATTR_TECHSPECH_RESUMEN_TAMANO'].fillna('vacio')
    if 'FILT_SISTEMA_OPERATIVO' in df.columns: df['FILT_SISTEMA_OPERATIVO'] = df['FILT_SISTEMA_OPERATIVO'].fillna('vacio')
    if 'ATTR_CONF_TIPOPLAN' in df.columns: df['ATTR_CONF_TIPOPLAN'] = df['ATTR_CONF_TIPOPLAN'].fillna('vacio')
    if 'ATTR_CHARS_EXT_A_DESC' in df.columns: df['ATTR_CHARS_EXT_A_DESC'] = df['ATTR_CHARS_EXT_A_DESC'].fillna('vacio')
    if 'ATTR_CHARS_EXT_B_DESC' in df.columns: df['ATTR_CHARS_EXT_B_DESC'] = df['ATTR_CHARS_EXT_B_DESC'].fillna('vacio')
    if 'ATTR_CHARS_EXT_C_DESC' in df.columns: df['ATTR_CHARS_EXT_C_DESC'] = df['ATTR_CHARS_EXT_C_DESC'].fillna('vacio')

    if 'NAME' in df.columns: df['NAME'] = df['NAME'].str.replace('\n', '-')
    if 'DESCRIPTION' in df.columns: df['DESCRIPTION'] = df['DESCRIPTION'].str.replace('\n', '-')
    if 'ATTR_CHARS_EXT_A_DESC' in df.columns: df['ATTR_CHARS_EXT_A_DESC'] = df['ATTR_CHARS_EXT_A_DESC'].str.replace('\n', '-')
    if 'ATTR_CHARS_EXT_B_DESC' in df.columns: df['ATTR_CHARS_EXT_B_DESC'] = df['ATTR_CHARS_EXT_B_DESC'].str.replace('\n', '-')
    if 'ATTR_CHARS_EXT_C_DESC' in df.columns: df['ATTR_CHARS_EXT_C_DESC'] = df['ATTR_CHARS_EXT_C_DESC'].str.replace('\n', '-')

    if 'NAME' in df.columns: df['NAME'] = df['NAME'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    if 'DESCRIPTION' in df.columns: df['DESCRIPTION'] = df['DESCRIPTION'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    if 'ATTR_CHARS_EXT_A_DESC' in df.columns: df['ATTR_CHARS_EXT_A_DESC'] = df['ATTR_CHARS_EXT_A_DESC'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    if 'ATTR_CHARS_EXT_B_DESC' in df.columns: df['ATTR_CHARS_EXT_B_DESC'] = df['ATTR_CHARS_EXT_B_DESC'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    if 'ATTR_CHARS_EXT_C_DESC' in df.columns: df['ATTR_CHARS_EXT_C_DESC'] = df['ATTR_CHARS_EXT_C_DESC'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

# Padres (pre, pos y otros)
df_products_base_codes = df_products.drop_duplicates(subset=['PRODUCT_CODE_TELV2'])
# Padres (plan fijo)
df_products_base_codes_plan_fijo = df_products_plan_fijo.drop_duplicates(subset=['PRODUCT_CODE'])
# Padres (plan)
df_products_base_codes_plan = df_products_options.drop_duplicates(subset=['PRODUCT_CODE'])

