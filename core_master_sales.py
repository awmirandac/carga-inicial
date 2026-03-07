import xml.etree.ElementTree as ET

########## FUNCIONES AUXILIARES ##########

def create_catalog_header(root):
    """Crea la cabecera del catálogo XML con configuración de imágenes"""
    header = ET.SubElement(root, 'header')
    image_settings = ET.SubElement(header, 'image-settings')

    # External location
    external_location = ET.SubElement(image_settings, 'external-location')
    ET.SubElement(external_location, 'http-url').text = EXTERNAL_LOCATION_HTTP
    ET.SubElement(external_location, 'https-url').text = EXTERNAL_LOCATION_HTTPS

    # View types
    view_types = ET.SubElement(image_settings, 'view-types')
    for view_type in ['swatch', 'small', 'medium', 'large']:
        ET.SubElement(view_types, 'view-type').text = view_type

    ET.SubElement(image_settings, 'alt-pattern').text = '${productName}'
    ET.SubElement(image_settings, 'title-pattern').text = '${productName}'

    # Root category
    category = ET.SubElement(root, 'category', {'category-id': 'root'})
    ET.SubElement(category, 'online-flag').text = 'true'

def add_basic_product_info(product, min_qty='1', step_qty='1'):
    """Añade elementos básicos comunes a todos los productos"""
    ET.SubElement(product, 'ean')
    ET.SubElement(product, 'upc')
    ET.SubElement(product, 'unit')
    ET.SubElement(product, 'min-order-quantity').text = min_qty
    ET.SubElement(product, 'step-quantity').text = step_qty

def add_product_flags(product, online=True, available=True, searchable=True):
    """Añade flags de disponibilidad del producto"""
    ET.SubElement(product, 'online-flag').text = str(online).lower()
    ET.SubElement(product, 'available-flag').text = str(available).lower()
    ET.SubElement(product, 'searchable-flag').text = str(searchable).lower()

def add_product_images(product, product_code):
    """Añade grupos de imágenes para un producto"""
    images = ET.SubElement(product, 'images')
    for img_type in ['small', 'medium', 'large']:
        image_group = ET.SubElement(images, 'image-group', {'view-type': img_type})
        if img_type == 'large':
            for i in range(1, 4):
                ET.SubElement(image_group, 'image', {'path': f'{product_code}/{product_code}_{i}_312x400.jpg'})
        else:
            ET.SubElement(image_group, 'image', {'path': f'{product_code}/{product_code}_1_210x180.jpg'})

def add_store_attributes(product):
    """Añade atributos de tienda con valores por defecto"""
    store_attrs = ET.SubElement(product, 'store-attributes')
    for flag in ['force-price-flag', 'non-inventory-flag', 'non-revenue-flag', 'non-discountable-flag']:
        ET.SubElement(store_attrs, flag).text = 'false'

def create_variation_attribute(attributes, attr_id, display_name, values):
    """Crea un atributo de variación con sus valores"""
    if len(values) == 0:
        return

    # Ordenar valores si es cen_modality: Prepago primero, luego Postpago
    if attr_id == 'cen_modality':
        values_list = list(values)
        sorted_values = []
        # Agregar PREPAGO primero si existe
        if 'PREPAGO' in values_list:
            sorted_values.append('PREPAGO')
        # Agregar POSPAGO después si existe
        if 'POSPAGO' in values_list:
            sorted_values.append('POSPAGO')
        # Agregar cualquier otro valor que no sea PREPAGO ni POSPAGO
        for v in values_list:
            if v not in ['PREPAGO', 'POSPAGO']:
                sorted_values.append(v)
        values = sorted_values

    variation_attr = ET.SubElement(attributes, 'variation-attribute', {
        'attribute-id': attr_id,
        'variation-attribute-id': attr_id
    })
    ET.SubElement(variation_attr, 'display-name', {'xml:lang': 'x-default'}).text = display_name
    variation_values = ET.SubElement(variation_attr, 'variation-attribute-values')

    for value in values:
        # Formatear valores específicos
        formatted_value = value
        if attr_id == 'cen_modality':
            if value == 'PREPAGO':
                formatted_value = 'Prepago'
            elif value == 'POSPAGO':
                formatted_value = 'Postpago'
            elif value == 'OTRO':
                formatted_value = 'Accesorios'

        variation_value = ET.SubElement(variation_values, 'variation-attribute-value', {'value': formatted_value})
        ET.SubElement(variation_value, 'display-value', {'xml:lang': 'x-default'}).text = formatted_value

def convert_values_custom_attribute(custom_attrs, attr_value, _attr_id):
    """Formatea y crea custom-attribute para cen_otherBenDataExtended con múltiples valores

    Transforma valores separados por saltos de línea o viñetas en elementos <value> individuales
    Ejemplo:
        Input: "Redes ilimitadas por 15 días\\n10GB de navegación\\nRecibe..."
        Output: <custom-attribute attribute-id="cen_otherBenDataExtended">
                  <value>Redes ilimitadas por 15 días</value>
                  <value>10GB de navegación</value>
                  ...
                </custom-attribute>
    """
    custom_attr = ET.SubElement(custom_attrs, 'custom-attribute', {'attribute-id': _attr_id})

    # Dividir por saltos de línea o guiones que indican nuevos beneficios
    values = [v.strip() for v in attr_value.replace('- ', '\n').split('\n') if v.strip()]

    # Crear elementos <value> para cada beneficio
    for value in values:
        ET.SubElement(custom_attr, 'value').text = value

def add_product_variations(product, df_prod_attr):
    """Añade variaciones (color, almacenamiento, modalidad) a un producto padre"""

    variations = ET.SubElement(product, 'variations')
    attributes = ET.SubElement(variations, 'attributes')

    # Separar por tipo de producto
    df_prepago_pospago = df_prod_attr[(df_prod_attr['ATTR_CONF_TIPOPRODUCTO'] == 'PREPAGO') | (df_prod_attr['ATTR_CONF_TIPOPRODUCTO'] == 'POSPAGO')]
    df_otro = df_prod_attr[df_prod_attr['ATTR_CONF_TIPOPRODUCTO'] == 'OTRO']

    # PREPAGO/POSPAGO: 3 variaciones (color, almacenamiento, modalidad)
    if not df_prepago_pospago.empty:
        create_variation_attribute(attributes, 'cen_color', 'Color', df_prepago_pospago['DEF_COLOR'].unique())
        create_variation_attribute(attributes, 'cen_storage', 'Almacenamiento', df_prepago_pospago['DEF_CAPACIDAD'].unique())
        create_variation_attribute(attributes, 'cen_modality', 'Modalidad', df_prepago_pospago['ATTR_CONF_TIPOPRODUCTO'].unique())

    # OTRO: solo variación de color
    if not df_otro.empty:
        create_variation_attribute(attributes, 'cen_color', 'Color', df_otro['DEF_COLOR'].unique())

    # SKUs de variantes (todos)
    variants = ET.SubElement(variations, 'variants')
    for idx, row in enumerate(df_prod_attr.iterrows()):
        _, product_row = row
        is_default = 'true' if idx == 0 else 'false'
        ET.SubElement(variants, 'variant', {
            'product-id': product_row['ITEM_CODE'],
            'default': is_default
        })

def convert_sns_data(custom_attrs, attr_value):
    """Formatea y crea custom-attribute para cen_snsData

    Transforma valores separados por comas en formato lowercase y unificado
    Ejemplo:
        Input: "Tiktok, WhatsApp, Facebook, Instagram, X"
        Output: <custom-attribute attribute-id="cen_snsData">whatsapp,facebook,instagram,tiktok,x</custom-attribute>
    """
    # Mapeo de variaciones de valores a su forma estándar
    sns_mapping = {
        'tiktok': 'tiktok',
        'whatsapp': 'whatsapp',
        'facebook': 'facebook',
        'instagram': 'instagram',
        'x': 'x',
        'waze': 'waze',
        'messenger': 'messenger',
        'uber': 'uber'
    }

    # Dividir por comas y normalizar cada valor
    raw_values = [v.strip().lower() for v in attr_value.split(',') if v.strip()]

    # Mapear valores a su forma estándar y eliminar duplicados
    sns_values = []
    for value in raw_values:
        # Buscar en el mapping (por si hay variaciones)
        if value in sns_mapping:
            sns_values.append(sns_mapping[value])

    # Eliminar duplicados manteniendo orden
    seen = set()
    unique_values = []
    for val in sns_values:
        if val not in seen:
            seen.add(val)
            unique_values.append(val)

    # Crear el custom-attribute con valores separados por coma
    sns_text = ','.join(unique_values)
    custom_attr = ET.SubElement(custom_attrs, 'custom-attribute', {'attribute-id': 'cen_snsData'})
    custom_attr.text = sns_text

def convert_boolean_analog_support(custom_attrs, attr_value):
    """Convierte valores booleanos para cen_sim_analogic_support

    Transforma "Yes" a "true" y "No" a "false"
    Ejemplo:
        Input: "Yes"
        Output: <custom-attribute attribute-id="cen_sim_analogic_support">true</custom-attribute>
    """
    # Convertir valores a booleano
    bool_value = 'true' if str(attr_value).lower() == 'yes' else 'false'
    custom_attr = ET.SubElement(custom_attrs, 'custom-attribute', {'attribute-id': 'cen_sim_analogic_support'})
    custom_attr.text = bool_value

def convert_boolean_esim_support(custom_attrs, attr_value):
    """Convierte valores booleanos para cen_esim_support.

    Transforma "Yes" a "true" y "No" a "false".
    """
    bool_value = 'true'
    custom_attr = ET.SubElement(custom_attrs, 'custom-attribute', {'attribute-id': 'cen_esim_support'})
    custom_attr.text = bool_value

def create_datasheet(custom_attrs):
    """Crea custom-attribute para cenDataSheet con HTML y CSS embebido

    Genera un custom-attribute con estilos CSS y estructura HTML para mostrar
    especificaciones técnicas del producto en formato de tarjetas
    """
    datasheet_html = '''<style type="text/css">.data-sheet-container { display: grid; gap: 22px; grid-template-columns: repeat(auto-fill, 436px); -webkit-box-pack: center; -ms-flex-pack: center; -webkit-justify-content: center; justify-content: center; } .data-sheet-element { width: 436px; margin-top: 22px; } .data-sheet-card-header { display: -webkit-box; display: -webkit-flex; display: -ms-flexbox; display: flex; gap: 8px; width: 100%; height: 56px; border-radius: 12px 12px 0px 0px; background-color: #F4F4F4; -webkit-box-pack: center; -ms-flex-pack: center; -webkit-justify-content: center; justify-content: center; -webkit-align-items: center; -webkit-box-align: center; -ms-flex-align: center; align-items: center; font-size: 16px; color: #3C3C3C; font-family: Roboto Medium; } .data-sheet-card-body { padding: 12px; } .data-sheet-card-body-row { display: -webkit-box; display: -webkit-flex; display: -ms-flexbox; display: flex; border-bottom: 1px solid #F4F4F4; margin-bottom: 0.5rem; padding-bottom: 0.5rem; } .data-sheet-card-body-title { width: 50%; font-size: 14px; line-height: 21px; font-weight: 400; color: #6C6C6C; } .data-sheet-card-body-description { width: 50%; font-size: 14px; line-height: 21px; font-weight: 400; color: #3C3C3C; } .data-sheet-card-body-subtitle-container { display: -webkit-box; display: -webkit-flex; display: -ms-flexbox; display: flex; border-bottom: 1px solid #F4F4F4; margin-bottom: 0.5rem; padding-bottom: 0.5rem; -webkit-box-pack: center; -ms-flex-pack: center; -webkit-justify-content: center; justify-content: center; } .data-sheet-card-body-subtitle-text { font-size: 16px; line-height: 21px; font-weight: 500; color: #3C3C3C; } @media (max-width: 1024px) { .data-sheet-container { grid-template-columns: repeat(auto-fill, 345px); } .data-sheet-element { width: 345px; } } </style> <div class="data-sheet-container"> <div class="css-0"> <div class="data-sheet-card"> <div class="data-sheet-card-header"><img alt="" src="Procesador.svg?$staticlink$" title="" /> <p>Procesador</p> </div> <div class="data-sheet-card-body"> <div class="data-sheet-card-body-row"> <p class="data-sheet-card-body-title">Modelo</p> <p class="data-sheet-card-body-description">{{c_attr_techspech_general_procesador}}</p> </div> <div class="data-sheet-card-body-row"> <p class="data-sheet-card-body-title">Sistema operativo</p> <p class="data-sheet-card-body-description">{{c_attr_techspech_general_sistema_operativo}}</p> </div> <div class="data-sheet-card-body-row"> <p class="data-sheet-card-body-title">Tipo de SIM</p> <p class="data-sheet-card-body-description">{{c_cen_esim_support}}</p> </div> <div class="data-sheet-card-body-row"> <p class="data-sheet-card-body-title">Testeo</p> <p class="data-sheet-card-body-description">{{testoooo}}</p> </div> </div> </div> <div class="data-sheet-card"> <div class="data-sheet-card-header"><img alt="Imagen de bluetooth" src="Conectividad.svg?$staticlink$" title="" /> <p>Conectividad</p> </div> <div class="data-sheet-card-body"> <div class="data-sheet-card-body-row"> <p class="data-sheet-card-body-title">Bluetooh</p> <p class="data-sheet-card-body-description">{{c_attr_techspech_conectividad_bluetooth}}</p> </div> <div class="data-sheet-card-body-row"> <p class="data-sheet-card-body-title">Estéreo Bluetooh</p> <p class="data-sheet-card-body-description">{{c_attr_techspech_conectividad_bluetooth_st}}</p> </div> <div class="data-sheet-card-body-row"> <p class="data-sheet-card-body-title">Wi-fi</p> <p class="data-sheet-card-body-description">{{c_attr_techspech_conectividad_wifi}}</p> </div> <div class="data-sheet-card-body-row"> <p class="data-sheet-card-body-title">GPS</p> <p class="data-sheet-card-body-description">{{c_attr_techspech_conectividad_gps}}</p> </div> <div class="data-sheet-card-body-row"> <p class="data-sheet-card-body-title">Bandas</p> <p class="data-sheet-card-body-description">{{c_attr_techspech_conectividad_banda}}</p> </div> <div class="data-sheet-card-body-row"> <p class="data-sheet-card-body-title">Tarjeta SIM</p> <p class="data-sheet-card-body-description">{{c_cen_esim_support}}</p> </div> </div> </div> </div> <div class="css-0"> <div class="data-sheet-card"> <div class="data-sheet-card-header"><img alt="" src="Chip.svg?$staticlink$" title="" /> <p>Memoria</p> </div> <div class="data-sheet-card-body"> <div class="data-sheet-card-body-row"> <p class="data-sheet-card-body-title">Almacenamiento</p> <p class="data-sheet-card-body-description">{{c_cen_storage}}</p> </div> </div> </div> <div class="data-sheet-card"> <div class="data-sheet-card-header"><img alt="" src="Camara.svg?$staticlink$" title="" /> <p>Cámara</p> </div> <div class="data-sheet-card-body"> <div class="data-sheet-card-body-row"> <p class="data-sheet-card-body-title">Cámara frontal</p> <p class="data-sheet-card-body-description">{{c_attr_techspech_entretenimiento_camara_frontal}}</p> </div> <div class="data-sheet-card-body-row"> <p class="data-sheet-card-body-title">Flash</p> <p class="data-sheet-card-body-description">{{c_attr_techspech_entretenimiento_flash}}</p> </div> <div class="data-sheet-card-body-row"> <p class="data-sheet-card-body-title">Enfoque</p> <p class="data-sheet-card-body-description">{{c_attr_techspech_entretenimiento_enfoque}}</p> </div> <div class="data-sheet-card-body-subtitle-container"> <p class="data-sheet-card-body-subtitle-text">Frontal</p> </div> <div class="data-sheet-card-body-row"> <p class="data-sheet-card-body-title">Resolución</p> <p class="data-sheet-card-body-description">{{c_attr_techspech_entretenimiento_camara_frontal}}</p> </div> <div class="data-sheet-card-body-subtitle-container"> <p class="data-sheet-card-body-subtitle-text">Trasera estándar</p> </div> </div> </div> <div class="data-sheet-card"> <div class="data-sheet-card-header"><img alt="Imagen de Caracteristicas" src="Caracteristicas.svg?$staticlink$" title="" /> <p>Características</p> </div> <div class="data-sheet-card-body"> <div class="data-sheet-card-body-row"> <p class="data-sheet-card-body-title">Video</p> <p class="data-sheet-card-body-description">{{c_attr_techspech_entretenimiento_video}}</p> </div> <div class="data-sheet-card-body-row"> <p class="data-sheet-card-body-title">Videollamada</p> <p class="data-sheet-card-body-description">{{c_attr_techspech_general_videollamada}}</p> </div> <div class="data-sheet-card-body-row"> <p class="data-sheet-card-body-title">Color</p> <p class="data-sheet-card-body-description">{{c_cen_color}}</p> </div> <div class="data-sheet-card-body-row"> <p class="data-sheet-card-body-title">Flash</p> <p class="data-sheet-card-body-description">{{c_attr_techspech_entretenimiento_flash}}</p> </div> </div> </div> </div> <div class="css-0"> <div class="data-sheet-card"> <div class="data-sheet-card-header"><img alt="Imagen de audio" src="Audio.svg?$staticlink$" title="" /> <p>Audio</p> </div> <div class="data-sheet-card-body"> <div class="data-sheet-card-body-row"> <p class="data-sheet-card-body-title">Música</p> <p class="data-sheet-card-body-description">{{c_attr_techspech_entretenimiento_musica}}</p> </div> </div> </div> <div class="data-sheet-card"> <div class="data-sheet-card-header"><img alt="Imagen de estrella" src="Diseño.svg?$staticlink$" title="" /> <p>Diseño</p> </div> <div class="data-sheet-card-body"> <div class="data-sheet-card-body-row"> <p class="data-sheet-card-body-title">Tamaño</p> <p class="data-sheet-card-body-description">{{c_attr_techspech_resumen_tamano}}</p> </div> <div class="data-sheet-card-body-row"> <p class="data-sheet-card-body-title">Peso</p> <p class="data-sheet-card-body-description">{{c_attr_techspech_resumen_peso}}</p> </div> <div class="data-sheet-card-body-row"> <p class="data-sheet-card-body-title">Dimensiones del teléfono</p> <p class="data-sheet-card-body-description">{{c_attr_techspech_general_dimensiones}}</p> </div> </div> </div> <div class="data-sheet-card"> <div class="data-sheet-card-header"><img alt="Imagen de batería" src="Bateria.svg?$staticlink$" title="" /> <p>Batería</p> </div> <div class="data-sheet-card-body"> <div class="data-sheet-card-body-row"> <p class="data-sheet-card-body-title">Capacidad de la batería</p> <p class="data-sheet-card-body-description">{{c_attr_techspech_general_bateria_capacidad}}</p> </div> </div> </div> </div> </div>'''

    custom_attr = ET.SubElement(custom_attrs, 'custom-attribute', {'attribute-id': 'cenDataSheet'})
    custom_attr.text = datasheet_html

def add_custom_attributes(product, row, df_columns):
    """Añade custom attributes del producto basados en prefijos"""
    custom_attrs = ET.SubElement(product, 'custom-attributes')

    # Atributos conocidos que no deben importarse como custom attributes
    skip_attrs = {'category_code', 'attr_conf_esim', 'attr_conf_tipo_sim'}

    for prefix in ATTR_PREFFIXES:
        for column_name in df_columns:
            if column_name.startswith(prefix) and not pd.isna(row[column_name]):
                attr_id = column_name.lower()
                if attr_id in skip_attrs:
                    continue
                attr_value = str(row[column_name])

                # Formatear modalidad
                if attr_id == 'cen_modality':
                    if attr_value == 'PREPAGO':
                        attr_value = 'Prepago'
                    elif attr_value == 'POSPAGO':
                        attr_value = 'Postpago'
                if attr_id == 'attr_conf_modalidad':
                    if attr_value == 'Prepago':
                        attr_value = 'PREPAGO'
                    elif attr_value == 'Postpago':
                        attr_value = 'POSTPAGO'
                    elif attr_value == 'Prepago y Postpago':
                        attr_value = 'PREPAGOPOSTPAGO'
                    elif attr_value == 'Planes postpago con equipo':
                        attr_value = 'PLANCONEQUIPO'
                    elif attr_value == 'Planes postpago sin equipo':
                        attr_value = 'PLANSINEQUIPO'
                    elif attr_value == 'Plan con y sin equipo':
                        attr_value = 'PLANCONEQUIPOPLANSINEQUIPO'
                    elif attr_value == 'Avanzado':
                        attr_value = 'AVANZADO' 
                    elif attr_value == 'Avanzado HD':
                        attr_value = 'AVANZADOHD'
                    elif attr_value == 'Avanzado HD Plus':
                        attr_value = 'AVANZADOHDPLUS'
                if attr_id == 'attr_conf_tipoproducto':
                    if attr_value == 'OTRO':
                        attr_value = 'ACCESORIOS'
                ET.SubElement(custom_attrs, 'custom-attribute', {'attribute-id': attr_id}).text = attr_value

    for prefix in CEN_PREFFIXES:
        for column_name in df_columns:
            if column_name.startswith(prefix) and column_name in row.index and not pd.isna(row[column_name]): # Added column_name in row.index check
                attr_id = column_name
                attr_value = str(row[column_name])

                # Formatear campos cen, excepto color, almacenamiento y modalidad
                if attr_id not in ['cen_color', 'cen_storage', 'cen_modality']:
                    if attr_id == 'cen_otherBenDataExtended':
                        convert_values_custom_attribute(custom_attrs, attr_value, attr_id)
                    elif attr_id == 'cen_outstanding_features':
                        convert_values_custom_attribute(custom_attrs, attr_value, attr_id)
                    elif attr_id == 'cen_snsData':
                        convert_sns_data(custom_attrs, attr_value)
                    elif attr_id == 'cen_sim_analogic_support':
                        convert_boolean_analog_support(custom_attrs, attr_value)
                    elif attr_id == 'c_cen_esim_support':
                        convert_boolean_esim_support(custom_attrs, attr_value)
                    else:
                        ET.SubElement(custom_attrs, 'custom-attribute', {'attribute-id': attr_id}).text = attr_value

    create_datasheet(custom_attrs)

def create_plan_options_for_phone(options, item_code, df_relations, df_plans):
    """Crea opciones de planes para un teléfono POSPAGO"""
    related_plans = df_relations[df_relations['ITEM_CODE'] == item_code]

    if related_plans.empty or len(related_plans) == 0:
        return

    # Crear product-option específico
    product_option = ET.SubElement(options, 'option', {'option-id': PRODUCT_OPTION_PLAN})
    ET.SubElement(product_option, 'sort-mode').text = 'price'
    option_values = ET.SubElement(product_option, 'option-values')

    # Eliminar duplicados por PLAN_CODE
    unique_plans = related_plans.drop_duplicates(subset=['PLAN_CODE'], keep='first')

    # Iterar sobre planes relacionados
    for idx_plan, plan_row in unique_plans.iterrows():
        plan_code = str(plan_row['PLAN_CODE'])
        offer_price = str(plan_row['OFFER_PRICE'])

        # Obtener nombre del plan
        plan_info = df_plans[df_plans['ITEM_CODE'] == plan_code]
        plan_name = plan_info['NAME'].values[0] if not plan_info.empty else plan_code

        # Determinar si es default
        is_default = 'true' if idx_plan == unique_plans.index[0] else 'false'

        option_value = ET.SubElement(option_values, 'option-value', {'value-id': plan_code, 'default': is_default})
        ET.SubElement(option_value, 'display-value', {'xml:lang': 'x-default'}).text = plan_name
        option_prices = ET.SubElement(option_value, 'option-value-prices')
        ET.SubElement(option_prices, 'option-value-price', {'currency': 'CRC'}).text = offer_price

def create_phone_options_for_plan(options, plan_code, df_relations, df_phones):
    """Crea opciones de teléfonos para un plan CON EQUIPO"""
    related_phones = df_relations[df_relations['PLAN_CODE'] == plan_code]

    if related_phones.empty or len(related_phones) == 0:
        return

    # Crear product-option específico para teléfonos
    product_option = ET.SubElement(options, 'option', {'option-id': 'planPostpagoTelefonoOptions'})
    ET.SubElement(product_option, 'sort-mode').text = 'position'
    option_values = ET.SubElement(product_option, 'option-values')

    # Eliminar duplicados por ITEM_CODE
    unique_phones = related_phones.drop_duplicates(subset=['ITEM_CODE'], keep='first')
    
    # Recolectar solo los códigos padres sin duplicados
    added_codes = set()
    idx_for_default = 0

    # Agregar solo los teléfonos padres
    for idx_phone, phone_row in unique_phones.iterrows():
        phone_code = str(phone_row['ITEM_CODE'])

        # Verificar existencia en df_phones
        if phone_code not in df_phones['ITEM_CODE'].values:
            continue

        # Buscar el padre
        parent_rows = df_phones[df_phones['ITEM_CODE'] == phone_code]
        if parent_rows.empty:
            continue
            
        parent_code = str(parent_rows.iloc[0].get('PRODUCT_CODE_TELV2', ''))
        if not parent_code:
            continue
            
        # Evitar duplicados
        if parent_code in added_codes:
            continue
            
        added_codes.add(parent_code)
        is_default = 'true' if idx_for_default == 0 else 'false'
        idx_for_default += 1

        option_value = ET.SubElement(option_values, 'option-value', {'value-id': parent_code, 'default': is_default})
        ET.SubElement(option_value, 'display-value', {'xml:lang': 'x-default'}).text = parent_code
        ET.SubElement(option_value, 'product-id-modifier').text = parent_code
        option_prices = ET.SubElement(option_value, 'option-value-prices')
        ET.SubElement(option_prices, 'option-value-price', {'currency': 'CRC'}).text = '0.00'
        
        # Agregar también los hijos de este padre
        children_phones = df_phones[df_phones['PRODUCT_CODE_TELV2'] == parent_code]
        for _, child_row in children_phones.iterrows():
            child_code = str(child_row['ITEM_CODE'])
            
            # Evitar duplicados de hijos
            if child_code in added_codes:
                continue
                
            added_codes.add(child_code)
            
            child_option_value = ET.SubElement(option_values, 'option-value', {'value-id': child_code, 'default': 'false'})
            ET.SubElement(child_option_value, 'display-value', {'xml:lang': 'x-default'}).text = child_code
            ET.SubElement(child_option_value, 'product-id-modifier').text = child_code
            child_option_prices = ET.SubElement(child_option_value, 'option-value-prices')
            ET.SubElement(child_option_prices, 'option-value-price', {'currency': 'CRC'}).text = '0.00'

def add_product_options(product, row, df_relations, df_plans, df_phones):
    """Añade opciones de producto según tipo (POSPAGO, PREPAGO, PLAN)"""
    tipo_producto = row['ATTR_CONF_TIPOPRODUCTO']

    if tipo_producto == 'POSPAGO':
        options = ET.SubElement(product, 'options')
        create_plan_options_for_phone(options, str(row['ITEM_CODE']), df_relations, df_plans)
        ET.SubElement(options, 'shared-option', {'option-id': 'postpagoOptions'})
        ET.SubElement(options, 'shared-option', {'option-id': 'mesesContratoOptions'})

    elif tipo_producto == 'PREPAGO':
        options = ET.SubElement(product, 'options')
        ET.SubElement(options, 'shared-option', {'option-id': 'prepagoOptions'})

    elif tipo_producto == 'PLAN':
        options = ET.SubElement(product, 'options')

        if row['CLASIFICACION'] == 'CON EQUIPO':
            create_phone_options_for_plan(options, str(row['ITEM_CODE']), df_relations, df_phones)
            ET.SubElement(options, 'shared-option', {'option-id': 'mesesContratoOptions'})
            ET.SubElement(options, 'shared-option', {'option-id': 'planConEquipoOptions'})

        elif row['CLASIFICACION'] == 'SIN EQUIPO':
            ET.SubElement(options, 'shared-option', {'option-id': 'planSinEquipoOptions'})
            ET.SubElement(options, 'shared-option', {'option-id': 'mesesContratoOptions'})

def create_product_options(parent, df_options, name):
    """Crea product options generales (shared options)"""
    product_option = ET.SubElement(parent, 'product-option', {'option-id': name})
    ET.SubElement(product_option, 'display-name', {'xml:lang': 'x-default'}).text = name
    option_values = ET.SubElement(product_option, 'option-values')

    for idx, row in enumerate(df_options.iterrows()):
        _, option_row = row
        is_default = 'true' if idx == 0 else 'false'
        option = ET.SubElement(option_values, 'option-value', {'value-id': str(option_row['OPTION_CODE']), 'default': is_default})
        ET.SubElement(option, 'display-value', {'xml:lang': 'x-default'}).text = str(option_row['OPTION_NAME'])
        option_prices = ET.SubElement(option, 'option-value-prices')
        ET.SubElement(option_prices, 'option-value-price', {'currency': 'CRC'}).text = str(option_row['OPTION_PRICE'])

########## CONSTRUCCIÓN DEL CATÁLOGO ##########

# Crear el elemento raíz del XML
root = ET.Element('catalog')
root.set('xmlns', 'http://www.demandware.com/xml/impex/catalog/2006-10-31')
root.set('catalog-id', MASTER_CATALOG_NAME)

# Crear cabecera
create_catalog_header(root)


########## CREACIÓN DE PRODUCTOS PADRES (CON VARIACIONES) ##########

def create_parent_product(root, row, df, df_children):
    """Crea un producto padre con sus variaciones"""
    # Determinar product-id según dataframe
    if df is df_products_base_codes:
        product_id = str(row['PRODUCT_CODE_TELV2'])
        display_name = row['NOMBRE_RESUMIDO'].replace('\n', '<br />')
    else:
        product_id = str(row['PRODUCT_CODE'])
        display_name = row['NAME'].replace('\n', '<br />')

    # Crear producto
    product = ET.SubElement(root, 'product', {'product-id': product_id})
    add_basic_product_info(product)

    # Display name y descripciones
    ET.SubElement(product, 'display-name', {'xml:lang': 'x-default'}).text = display_name
    ET.SubElement(product, 'short-description', {'xml:lang': 'x-default'}).text = str(row['ATTR_CHARS_EXT_A_DESC'])
    long_desc = f"{row['ATTR_CHARS_EXT_A_DESC']} {row['ATTR_CHARS_EXT_B_DESC']} {row['ATTR_CHARS_EXT_C_DESC']}"
    ET.SubElement(product, 'long-description', {'xml:lang': 'x-default'}).text = str(long_desc)

    add_product_flags(product)
    add_product_images(product, row['ITEM_CODE'])

    ET.SubElement(product, 'brand').text = str(row['FILT_MARCA'])
    
    custom_attrs = ET.SubElement(product, 'custom-attributes')
    ET.SubElement(custom_attrs, 'custom-attribute', {'attribute-id': 'attr_texto_cuotas'}).text = str(row['ATTR_TEXTO_CUOTAS'])

    add_product_variations(product, df_children)
    add_store_attributes(product)

dataframes_base_codes = [df_products_base_codes, df_products_base_codes_plan_fijo, df_products_base_codes_plan]
for df in dataframes_base_codes:
    for _, row in df.iterrows():
        # Obtener hijos del producto padre
        if df is df_products_base_codes:
            df_children = df_products[df_products['PRODUCT_CODE_TELV2'] == row['PRODUCT_CODE_TELV2']]
        elif df is df_products_base_codes_plan_fijo:
            df_children = df_products_plan_fijo[df_products_plan_fijo['PRODUCT_CODE'] == row['PRODUCT_CODE']]
        else:
            df_children = df_products_options[df_products_options['PRODUCT_CODE'] == row['PRODUCT_CODE']]

        create_parent_product(root, row, df, df_children)


########## CREACIÓN DE PRODUCTOS INDIVIDUALES (HIJOS) ##########

def create_child_product(root, row, df_columns):
    """Crea un producto individual (hijo/variante)"""
    product = ET.SubElement(root, 'product', {'product-id': str(row['ITEM_CODE'])})
    add_basic_product_info(product)

    # Display name y descripciones
    ET.SubElement(product, 'display-name', {'xml:lang': 'x-default'}).text = row['NAME']
    ET.SubElement(product, 'short-description', {'xml:lang': 'x-default'}).text = str(row['ATTR_CHARS_EXT_A_DESC'])
    long_desc = f"{row['ATTR_CHARS_EXT_A_DESC']} {row['ATTR_CHARS_EXT_B_DESC']} {row['ATTR_CHARS_EXT_C_DESC']}"
    ET.SubElement(product, 'long-description', {'xml:lang': 'x-default'}).text = str(long_desc)

    add_product_flags(product)
    # Agregar imágenes si es PLAN, si no es variante no agrega imágenes
    if row['ATTR_CONF_TIPOPRODUCTO'] == 'PLAN':
        add_product_images(product, row['ITEM_CODE'])

    ET.SubElement(product, 'brand').text = str(row['FILT_MARCA'])

    # Custom attributes
    add_custom_attributes(product, row, df_columns)

    # Product options
    add_product_options(product, row, df_products_master_relations_phone_plan,
                       df_products_options, df_products)

    # Store attributes
    add_store_attributes(product)

dataframes_base = [df_products, df_products_plan_fijo, df_products_options]
for df in dataframes_base:
    for _, row in df.iterrows():
        create_child_product(root, row, df_products.columns)


########## CREACIÓN DE PRODUCT OPTIONS GENERALES (SHARED) ##########

# Definir opciones compartidas
shared_options = {
    'prepagoOptions': {
        'OPTION_CODE': ['PRLN'],
        'OPTION_NAME': ['Línea Nueva'],
        'OPTION_PRICE': [10.00]
    },
    'postpagoOptions': {
        'OPTION_CODE': ['PPLN', 'PPR'],
        'OPTION_NAME': ['Línea Nueva', 'Renueva tu equipo'],
        'OPTION_PRICE': [0.00, 0.00]
    },
    'mesesContratoOptions': {
        'OPTION_CODE': ['12', '18', '24'],
        'OPTION_NAME': ['12 meses', '18 meses', '24 meses'],
        'OPTION_PRICE': [0.00, 0.00, 0.00]
    },
    'planConEquipoOptions': {
        'OPTION_CODE': ['PCELN', 'PCERP'],
        'OPTION_NAME': ['Línea nueva', 'Renueva tu plan'],
        'OPTION_PRICE': [0.00, 0.00]
    },
    'planSinEquipoOptions': {
        'OPTION_CODE': ['PSELN', 'PSER'],
        'OPTION_NAME': ['Línea nueva', 'Renovación'],
        'OPTION_PRICE': [0.00, 0.00]
    }
}

# Crear cada shared option
for option_name, option_data in shared_options.items():
    create_product_options(root, pd.DataFrame(option_data), option_name)

########## EXPORTAR XML ##########
tree = ET.ElementTree(root)
tree.write('carganueva-master.xml', encoding='utf-8', xml_declaration=True)
print(tree)