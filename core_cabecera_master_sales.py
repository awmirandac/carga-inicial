# Constantes
MASTER_CATALOG_NAME = 'GT-claro-master'
SALES_CATALOG_NAME = 'GT-claro-sales'

EXTERNAL_LOCATION_HTTP = 'http://tiendaenlinea.claro.com.gt/cdn/'
EXTERNAL_LOCATION_HTTPS = 'https://tiendaenlinea.claro.com.gt/cdn/'

ATTR_PREFFIXES = ['ATTR_CHARS_', 'ATTR_TECHSPECH_', 'ATTR_CONF_', 'ATTR_DETALLE_', 'CEN_COLOR', 'CEN_STORAGE', 'CEN_MODALITY', 'CATEGORY_CODE', 'attr_conf_modalidad']
CEN_PREFFIXES = ['cen_']

PRODUCT_OPTION_PLAN = 'planesPostpagoOptions'

########################################################################################################################################

import pandas as pd
from google.colab import drive
drive.mount('/content/drive')
FOLDER = "/content/drive/MyDrive/Test_cargas_iniciales/Pruebas-DEV/02-03-2026/"

df_products_master = pd.read_csv(FOLDER + "[today]Item_master_actualizado_final.csv")
df_products_master_plan = pd.read_csv(FOLDER + "[today]item_Master_Planes.csv")
df_products_master_relations_phone_plan = pd.read_csv(FOLDER + "[today]Relations-Phone_Plan-PRIORIDAD_PHONE.csv")
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

########################################################################################################################################

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

