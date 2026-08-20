# %% Catalogo de ventas: categorias
import xml.etree.ElementTree as ET


# df_sales_categories se carga en la cabecera desde la pestana CATEGORY_SALES


# Crear el elemento raíz del XML
root = ET.Element('catalog')
root.set('xmlns', 'http://www.demandware.com/xml/impex/catalog/2006-10-31')
root.set('catalog-id', SALES_CATALOG_NAME)


# Crear el elemento 'header'
header = ET.SubElement(root, 'header')


# Crear el elemento 'image-settings' dentro de 'header'
image_settings = ET.SubElement(header, 'image-settings')


# Crear elementos dentro de 'image-settings'
external_location = ET.SubElement(image_settings, 'external-location')
ET.SubElement(external_location, 'http-url').text = EXTERNAL_LOCATION_HTTP
ET.SubElement(external_location, 'https-url').text = EXTERNAL_LOCATION_HTTPS


view_types = ET.SubElement(image_settings, 'view-types')
for view_type in ['large', 'medium', 'small', 'swatch']:
    view = ET.SubElement(view_types, 'view-type')
    view.text = view_type


ET.SubElement(image_settings, 'alt-pattern').text = '${productname}'
ET.SubElement(image_settings, 'title-pattern').text = '${productname}'


# Crear los elementos 'category'
categories = [
    {
        "category-id": "root",
        "display-name": "Sales Catalog",
        "custom-attributes": [
            {"attribute-id": "enableCompare", "value": "false"},
            {"attribute-id": "showInMenu", "value": "true"}
        ],
        "refinement-definitions": [
            {
                "type": "attribute",
                "bucket-type": "none",
                "attribute-id": "attr_tipo_tecnologia",
                "system": "false"
            },
            {
                "type": "attribute",
                "bucket-type": "none",
                "attribute-id": "attr_conf_modalidad",
                "system": "false"
            },
            {
                "type": "attribute",
                "bucket-type": "none",
                "attribute-id": "attr_chars_titulo_internet",
                "system": "false"
            },
            {
                "type": "attribute",
                "bucket-type": "none",
                "attribute-id": "brand",
                "system": "true",
                "display-name": "Marca",
                "value-set": "search-result",
                "sort-mode": "value-name",
                "sort-direction": "ascending",
                "cutoff-threshold": "5"
            },
            {
                "type": "attribute",
                "bucket-type": "none",
                "attribute-id": "cenPromotions",
                "system": "false",
                "display-name": "Promociones",
                "value-set": "search-result",
                "sort-mode": "value-name",
                "sort-direction": "ascending",
                "cutoff-threshold": "5"
            },
            {
                "type": "promotion",
                "bucket-type": "none",
                "display-name": "Promociones",
                "sort-mode": "value-count",
                "sort-direction": "ascending",
                "cutoff-threshold": "5"
            },
            {
                "type": "attribute",
                "bucket-type": "values",
                "attribute-id": "cen_storage",
                "system": "false",
                "display-name": "Capacidad de almacenamiento",
                "value-set": "search-result",
                "sort-mode": "value-name",
                "sort-direction": "ascending",
                "unbucketed-values-mode": "show-values",
                "cutoff-threshold": "5"
            },
            {
                "type": "attribute",
                "bucket-type": "none",
                "attribute-id": "cen_color",
                "system": "false",
                "display-name": "Color",
                "value-set": "search-result",
                "sort-mode": "value-name",
                "sort-direction": "ascending",
                "cutoff-threshold": "5"
            },
            {
                "type": "attribute",
                "bucket-type": "none",
                "attribute-id": "cenReleaseYear",
                "system": "false",
                "display-name": "Año",
                "value-set": "search-result",
                "sort-mode": "value-name",
                "sort-direction": "ascending",
                "cutoff-threshold": "5"
            },
            {
                "type": "price",
                "bucket-type": "none",
                "display-name": "Precio",
                "sort-mode": "value-count",
                "sort-direction": "ascending",
                "cutoff-threshold": "0"
            }
        ]
    }
]


# Función para agregar atributos personalizados
def add_custom_attributes(parent_element, attributes):
    custom_attributes = ET.SubElement(parent_element, 'custom-attributes')
    for attr in attributes:
        ET.SubElement(custom_attributes, 'custom-attribute', {'attribute-id': attr['attribute-id']}).text = attr['value']


# Función para agregar definiciones de refinamiento
def add_refinement_definitions(parent_element, definitions):
    refinement_definitions = ET.SubElement(parent_element, 'refinement-definitions')
    for definition in definitions:
        refinement_def = ET.SubElement(refinement_definitions, 'refinement-definition')
        for key, value in definition.items():
            if key == 'bucket-definitions':
                bucket_defs = ET.SubElement(refinement_def, 'bucket-definitions')
                for bucket in value:
                    bucket_elem = ET.SubElement(bucket_defs, 'price-bucket')
                    bucket_elem.set('currency', bucket['currency'])
                    ET.SubElement(bucket_elem, 'display-name', {'xml:lang':'x-default'}).text = bucket['display-name']
                    ET.SubElement(bucket_elem, 'threshold').text = bucket['threshold']
            elif key == 'type' or key == 'bucket-type' or key == 'system' or key == 'attribute-id':
              refinement_def.set(key, value)
            elif key == 'display-name':
              ET.SubElement(refinement_def, key, {'xml:lang':'x-default'}).text = value
            else :
              ET.SubElement(refinement_def, key).text = str(value)


# AMC-COMMENT: Creacion de categoria root
for category in categories:
  category_elem = ET.SubElement(root, 'category', {'category-id': category['category-id']})
  ET.SubElement(category_elem, 'display-name', attrib={'xml:lang': 'x-default'}).text = category['display-name']
  ET.SubElement(category_elem, 'online-flag').text = 'true'
  add_custom_attributes(category_elem, category.get('custom-attributes', []))
  add_refinement_definitions(category_elem, category.get('refinement-definitions', []))


# AMC-COMMENT: Definir estructura de árbol de categorías desde la pestana CATEGORY_SALES
# La hoja es la fuente de verdad: cada fila declara su NAME y de quien cuelga en PARENT_CODE.
category_hierarchy = {}
category_descriptions = {}

for index, category in df_sales_categories.iterrows():
    category_name = str(category['NAME'])
    parent_code = category['PARENT_CODE']
    category_hierarchy[category_name] = 'root' if pd.isna(parent_code) else str(parent_code)

    if pd.notna(category['DESCRIPTION']):
        category_descriptions[category_name] = str(category['DESCRIPTION'])

# AMC-COMMENT: Las ramas principales que solo figuran como PARENT_CODE (sin fila propia
# en la hoja) se deducen y cuelgan de root
for parent_code in df_sales_categories['PARENT_CODE'].dropna().unique():
    if str(parent_code) not in category_hierarchy:
        category_hierarchy[str(parent_code)] = 'root'


def profundidad_de_categoria(categoria):
    """Cuantos niveles hay entre la categoria y root."""
    niveles = 0
    visitadas = set()
    while categoria in category_hierarchy and categoria not in visitadas:
        visitadas.add(categoria)
        categoria = category_hierarchy[categoria]
        niveles += 1
    return niveles


# AMC-COMMENT: Creacion de categorias (<category category-id="col.NAME">)
# Se emiten de la mas general a la mas especifica para que el padre exista antes que el hijo
for category_name in sorted(category_hierarchy, key=lambda nombre: (profundidad_de_categoria(nombre), nombre)):
    category_elem = ET.SubElement(root, 'category', {'category-id': category_name})
    ET.SubElement(category_elem, 'display-name', attrib={'xml:lang': 'x-default'}).text = category_name

    # Agregar description si la hoja la trae
    if category_name in category_descriptions:
        ET.SubElement(category_elem, 'description', attrib={'xml:lang': 'x-default'}).text = category_descriptions[category_name]

    ET.SubElement(category_elem, 'online-flag').text = 'true'
    ET.SubElement(category_elem, 'parent').text = category_hierarchy[category_name]

    # Agregar elementos vacíos
    ET.SubElement(category_elem, 'template')
    ET.SubElement(category_elem, 'page-attributes')

    add_custom_attributes(category_elem,  [
            {"attribute-id": "enableCompare", "value": "false"},
            {"attribute-id": "showInMenu", "value": "true"}
        ])


# %% Asignacion de productos a categorias

# df_products: df de pre, pos y otros
    # df_prepago_pospago: df de pre y pospago
    # df_otros: df de otros (accesorios)
# df_products_plan_fijo: df solo de plan fijo
# df_products_options: df solo de planes

df_prepago_pospago = df_products[(df_products['ATTR_CONF_TIPOPRODUCTO'] == 'PREPAGO') | (df_products['ATTR_CONF_TIPOPRODUCTO'] == 'POSPAGO')]
df_otro = df_products[df_products['ATTR_CONF_TIPOPRODUCTO'] == 'OTRO']

def cadena_de_categorias(categoria):
    """Devuelve la categoria y todos sus ancestros segun el arbol, de la mas general a la mas especifica.

    Camina category_hierarchy hacia arriba hasta root (root no se asigna).
    """
    cadena = []
    actual = categoria
    while actual and actual != 'root' and actual not in cadena:
        cadena.append(actual)
        actual = category_hierarchy.get(actual)

    return list(reversed(cadena))


def categorias_de_producto(category_code):
    """Devuelve todas las categorias del arbol a las que pertenece un producto.

    El CATEGORY_CODE es la ruta de la categoria hoja
    ('equipos-y-accesorios/accesorio-movil/audifonos') y una celda puede traer
    varias rutas separadas por salto de linea. De cada ruta se toma la hoja y se
    expande su rama completa. El resultado va de la mas general a la mas especifica.
    """
    if pd.isna(category_code):
        return []

    resultado = []
    for ruta in str(category_code).split('\n'):
        segmentos = [s for s in ruta.strip().split('/') if s]
        if not segmentos:
            continue
        for categoria in cadena_de_categorias(segmentos[-1]):
            if categoria not in resultado:
                resultado.append(categoria)

    return resultado


def asignar_productos(df, columna_producto):
    """Asigna cada producto a su categoria hoja y a todos sus niveles superiores."""
    asignados = set()
    primarios = set()

    for index, row in df.iterrows():
        product_id = str(row[columna_producto])

        for categoria in categorias_de_producto(row['CATEGORY_CODE']):
            if (categoria, product_id) in asignados:
                continue
            asignados.add((categoria, product_id))

            category_assignment = ET.SubElement(root, 'category-assignment')
            category_assignment.set('category-id', categoria)
            category_assignment.set('product-id', product_id)

            # Un producto solo puede tener una categoria primaria: la rama principal
            if product_id not in primarios:
                primarios.add(product_id)
                ET.SubElement(category_assignment, 'primary-flag').text = 'true'


# Telefonos: el producto padre y cada variante van a la categoria de modalidad y a telefono
asignar_productos(df_prepago_pospago, 'PRODUCT_CODE_TELV2')
asignar_productos(df_prepago_pospago, 'ITEM_CODE')

# Accesorios, plan fijo y planes: solo el producto hijo
asignar_productos(df_otro, 'ITEM_CODE')
asignar_productos(df_products_plan_fijo, 'ITEM_CODE')
asignar_productos(df_products_options, 'ITEM_CODE')


# %% Exportar XML
# Crear el árbol XML y escribirlo en un archivo
tree = ET.ElementTree(root)
tree.write('NI-cargaX-sales.xml', encoding='utf-8', xml_declaration=True)

