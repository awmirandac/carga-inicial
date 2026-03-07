import xml.etree.ElementTree as ET


df_sales_categories = pd.read_csv(FOLDER + "[today_vf]category_sales.csv")


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


# AMC-COMMENT: Definir estructura de árbol de categorías
category_hierarchy = {
    'prepago': 'telefono',
    'postpago': 'telefono',
    'con-equipo': 'planes-postpago',
    'sin-equipo': 'planes-postpago',
    'accesorio-movil': 'equipos-y-accesorios',
    'equipos-claro-hogar': 'equipos-y-accesorios',
    'claro-hogar-doble': 'planes-claro-hogar',
    'claro-hogar-triple': 'planes-claro-hogar',
    'internet-fijo-inalambrico': 'planes-claro-hogar',
    'telefono': 'root',
    'planes-postpago': 'root',
    'equipos-y-accesorios': 'root',
    'planes-claro-hogar': 'root',
    'adaptadores-y-cables': 'accesorio-movil',
    'audifonos': 'accesorio-movil',
    'banda': 'accesorio-movil',
    'smartwatchs': 'accesorio-movil',
    'consolas-gaming': 'equipos-claro-hogar',
    'controles': 'equipos-claro-hogar',
    'laptops': 'equipos-claro-hogar',
    'ultra-wifi': 'equipos-claro-hogar'
}

# AMC-COMMENT: Crear categorías principales (telefono, planes-postpago, equipos-y-accesorios, planes-claro-hogar)
main_categories = [
    {'name': 'telefono', 'display-name': 'Teléfonos', 'description': 'Categoría de teléfonos'},
    {'name': 'planes-postpago', 'display-name': 'Planes Postpago', 'description': 'Categoría de planes postpago'},
    {'name': 'equipos-y-accesorios', 'display-name': 'Equipos y Accesorios', 'description': 'Categoría de equipos y accesorios'},
    {'name': 'planes-claro-hogar', 'display-name': 'Planes Claro Hogar', 'description': 'Categoría de planes Claro Hogar'}
]

for main_cat in main_categories:
    category_elem = ET.SubElement(root, 'category', {'category-id': main_cat['name']})
    ET.SubElement(category_elem, 'display-name', attrib={'xml:lang': 'x-default'}).text = main_cat['display-name']
    ET.SubElement(category_elem, 'description', attrib={'xml:lang': 'x-default'}).text = main_cat['description']
    ET.SubElement(category_elem, 'online-flag').text = 'true'
    ET.SubElement(category_elem, 'parent').text = 'root'
    ET.SubElement(category_elem, 'template')
    ET.SubElement(category_elem, 'page-attributes')
    add_custom_attributes(category_elem, [
        {"attribute-id": "enableCompare", "value": "false"},
        {"attribute-id": "showInMenu", "value": "true"}
    ])

# AMC-COMMENT: Creacion de categorias independientes (<category category-id="col.NAME">)
# Crear elementos 'category' en el XML (excluyendo las categorías principales ya creadas)
main_category_names = ['telefono', 'planes-postpago', 'equipos-y-accesorios', 'planes-claro-hogar']

for index, category in df_sales_categories.iterrows():
    category_name = category['NAME']
    
    # Saltar si es una categoría principal (ya fue creada)
    if category_name in main_category_names:
        continue
    
    category_elem = ET.SubElement(root, 'category', {'category-id': category_name})
    ET.SubElement(category_elem, 'display-name', attrib={'xml:lang': 'x-default'}).text = category_name
    
    # Agregar description si existe
    if pd.notna(category['DESCRIPTION']):
        ET.SubElement(category_elem, 'description', attrib={'xml:lang': 'x-default'}).text = str(category['DESCRIPTION'])
    
    ET.SubElement(category_elem, 'online-flag').text = 'true'

    # Agregar parent según la jerarquía definida
    if category_name in category_hierarchy:
        ET.SubElement(category_elem, 'parent').text = category_hierarchy[category_name]
    else:
        # Si no está en la jerarquía, usar 'root' por defecto
        ET.SubElement(category_elem, 'parent').text = 'root'
    
    # Agregar elementos vacíos
    ET.SubElement(category_elem, 'template')
    ET.SubElement(category_elem, 'page-attributes')

    add_custom_attributes(category_elem,  [
            {"attribute-id": "enableCompare", "value": "false"},
            {"attribute-id": "showInMenu", "value": "true"}
        ])


# df_products: df de pre, pos y otros
# df_products_plan_fijo: df solo de plan fijo
# df_products_options: df solo de planes


merged_df = pd.merge(df_products, df_sales_categories, on='CATEGORY_CODE', how='inner')

# AMC-COMMENT: Eliminar duplicados basados en PRODUCT_CODE_TELV2 y categoria para evitar asignaciones repetidas
merged_df_unique = merged_df.drop_duplicates(subset=['PRODUCT_CODE_TELV2', 'NAME_y'], keep='first')

# AMC-COMMENT: Asigna cada producto a una categoria especifica (<category-assignment category-id="col.NAME" product-id="ABC123">)
for index, row in merged_df_unique.iterrows():
    category_assignment = ET.SubElement(root, 'category-assignment')
    category_assignment.set('category-id', row['NAME_y'])
    category_assignment.set('product-id', row['PRODUCT_CODE_TELV2'])
    ET.SubElement(category_assignment, 'primary-flag').text = 'true'


merged_df_plan_fijo = pd.merge(df_products_plan_fijo, df_sales_categories, on='CATEGORY_CODE', how='inner')


# AMC-COMMENT: Asigna cada producto a una categoria especifica (<category-assignment category-id="col.NAME" product-id="ABC123">)
for index, row in merged_df_plan_fijo.iterrows():
    category_assignment = ET.SubElement(root, 'category-assignment')
    category_assignment.set('category-id', row['NAME_y'])
    category_assignment.set('product-id', row['ITEM_CODE'])
    ET.SubElement(category_assignment, 'primary-flag').text = 'true'


merged_df_plan = pd.merge(df_products_options, df_sales_categories, on='CATEGORY_CODE', how='inner')


# AMC-COMMENT: Asigna cada producto a una categoria especifica (<category-assignment category-id="col.NAME" product-id="ABC123">)
for index, row in merged_df_plan.iterrows():
    category_assignment = ET.SubElement(root, 'category-assignment')
    category_assignment.set('category-id', row['NAME_y'])
    category_assignment.set('product-id', row['ITEM_CODE'])
    ET.SubElement(category_assignment, 'primary-flag').text = 'true'




# Crear el árbol XML y escribirlo en un archivo
tree = ET.ElementTree(root)
tree.write('carganueva-sales.xml', encoding='utf-8', xml_declaration=True)

