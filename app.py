import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(
    page_title="SuperMarket",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded",
)
# -----------------------------------------------------------------------------------------------------------------------------
# Estilo de pagina y background

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: ("589.jpg");
background-size: 180%;
background-position: top left;
background-repeat: repeat;
background-attachment: local;
}}

[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}

[data-testid="stToolbar"] {{
right: 2rem;
}}

[data-testid="stSidebar"] {{
background: rgba(28,28,56,1);
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# -----------------------------------------------------------------------------------------------------------------------------
# Funciones predefinidas para Frontend


def centrar_imagen(imagen, ancho):
    # Aplicar estilo CSS para centrar la imagen con Markdown
    st.markdown(
        f'<div style="display: flex; justify-content: center;">'
        f'<img src="{imagen}" width="{ancho}">'
        f'</div>',
        unsafe_allow_html=True
    )


def centrar_texto(texto, tamanho, color):
    st.markdown(f"<h{tamanho} style='text-align: center; color: {color}'>{texto}</h{tamanho}>",
                unsafe_allow_html=True)

# -----------------------------------------------------------------------------------------------------------------------------

# Funciones de backend
# Conectar a la base de datos


def conectar_base(base):
    con = sqlite3.connect(base)
    cur = con.cursor()
    return con, cur


def base_ventas():
    con = sqlite3.connect('ventas.db')
    cur = con.cursor()

    # Verificar si la tabla ya existe
    cur.execute("PRAGMA table_info(ventas);")
    if not cur.fetchall():
        # La tabla no existe, la creamos
        cur.execute('''CREATE TABLE IF NOT EXISTS ventas
                    (id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo INTEGER,
                    producto VARCHAR(200) NOT NULL,
                    cantidad INTEGER NOT NULL,
                    FOREIGN KEY (codigo) REFERENCES stock(codigo))''')
    return con, cur


def base_precios():
    con = sqlite3.connect('precios.db')
    cur = con.cursor()

    # Verificar si la tabla ya existe
    cur.execute("PRAGMA table_info(precios);")
    if not cur.fetchall():
        # La tabla no existe, la creamos
        cur.execute('''CREATE TABLE IF NOT EXISTS precios
                (id_precio INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo INTEGER,
                producto VARCHAR(200) NOT NULL,
                precio_compra REAL,
                precio_venta REAL,
                FOREIGN KEY (codigo, producto) REFERENCES stock(codigo, producto))''')

    return con, cur


def base_stock():
    con = sqlite3.connect('stock.db')
    cur = con.cursor()

    # Verificar si la tabla ya existe
    cur.execute("PRAGMA table_info(stock);")
    if not cur.fetchall():
        # La tabla no existe, la creamos
        cur.execute('''CREATE TABLE IF NOT EXISTS stock
                    (codigo INTEGER PRIMARY KEY AUTOINCREMENT,
                    producto VARCHAR(200) NOT NULL,
                    cantidad INTEGER NOT NULL)''')
    return con, cur

# Mostrar datos de la base de datos


def mostrar_db(base):
    con, cur = conectar_base(base)
    data = cur.execute(f'SELECT * FROM {base} ORDER BY codigo')
    st.dataframe(data,
                 width=700,
                 hide_index=True)

# Agregar datos a la base de datos


def agregar_ventas(producto, cantidad, status):
    if not status:
        # Conectar a la base de datos "stock.db"
        con_stock, cur_stock = base_stock()

        # Verificar si existe el producto
        cur_stock.execute(
            "SELECT codigo FROM stock WHERE producto=?", (producto,))
        result_3 = cur_stock.fetchone()

        if result_3 is not None:
            codigo = result_3[0]

            # Conectar a la base de datos "ventas.db"
            con, cur = base_ventas()

            # Insertar datos en la tabla
            cur.execute('INSERT INTO ventas (codigo, producto, cantidad) VALUES (?, ?, ?)',
                        (codigo, producto, cantidad))
            con.commit()
            con.close()
        else:
            st.warning(f"No se encontró el producto {producto} en el stock. La venta no se registró.", icon="⚠️")
    else:
        st.info(f"La venta del producto {producto} fue cancelada y no se registró en el stock.", icon="ℹ️")


def agregar_precio(producto_2, precio_compra, precio_venta):
    # Conectar a la base de datos "stock.db"
    con_stock, cur_stock = base_stock()

    # Verificar si existe el producto
    cur_stock.execute(
        "SELECT codigo FROM stock WHERE producto=?", (producto_2,))
    result_3 = cur_stock.fetchone()

    codigo = result_3[0]

    # Conectar a la base de datos "precios.db"
    con_precios, cur_precios = base_precios()

    # Insertar datos en la tabla precios
    cur_precios.execute('INSERT INTO precios (codigo, producto, precio_compra, precio_venta) '
                        'VALUES (?, ?, ?, ?)',
                        (codigo, producto_2, precio_compra, precio_venta))

    con_precios.commit()
    con_stock.close()
    con_precios.close()


def modificar_precio(producto_2, precio_compra, precio_venta):
    # Conectar a la base de datos "precios.db"
    con_precios, cur_precios = base_precios()

    # Actualizar datos en la tabla precios
    cur_precios.execute('UPDATE precios SET precio_compra=?, precio_venta=? WHERE producto=?',
                        (precio_compra, precio_venta, producto_2))

    con_precios.commit()
    con_precios.close()

# Agregar datos a la base de datos


def agregar_productos(producto_1, cantidad_1):
    con, cur = base_stock()
    # Insertar datos en la tabla
    cur.execute('INSERT INTO stock (producto, cantidad) VALUES (?, ?)',
                (producto_1, cantidad_1))
    con.commit()
    st.caption(f"Se han agregado {cantidad_1} unidades del producto {producto_1}. Stock: {cantidad_1}")
    con.close()

# Agregar datos a la base de datos


def quitar_productos(producto, cantidad):
    con = sqlite3.connect('stock.db')
    cur = con.cursor()

    # Verificar si hay suficiente stock del producto
    cur.execute("SELECT cantidad FROM stock WHERE producto=?", (producto,))
    result = cur.fetchone()

    if result is None:
        st.warning(f"No se encontró el producto {producto} en el stock.")
    else:
        stock_actual = result[0]
        if stock_actual < cantidad:
            st.warning(f"No hay suficiente stock del producto {producto}. Stock actual: {stock_actual}")
        else:
            # Actualizar el stock restando la cantidad vendida
            nuevo_stock = stock_actual - cantidad
            cur.execute("UPDATE stock SET cantidad=? WHERE producto=?",
                        (nuevo_stock, producto))
            # Confirmar los cambios en la base de datos
            con.commit()
            st.success(f"Se han descontado {cantidad} unidades del producto {producto}. Nuevo stock: {nuevo_stock}")

    con.close()


def sumar_productos(producto_1, cantidad_1):
    con = sqlite3.connect('stock.db')
    cur = con.cursor()

    # Verificar si hay suficiente stock del producto
    cur.execute("SELECT cantidad FROM stock WHERE producto=?", (producto_1,))
    result_2 = cur.fetchone()

    stock_actual = result_2[0]
    nuevo_stock_2 = stock_actual + cantidad_1
    cur.execute("UPDATE stock SET cantidad=? WHERE producto=?",
                (nuevo_stock_2, producto_1))
    # Confirmar los cambios en la base de datos
    con.commit()
    st.caption(f"Se han sumado {cantidad_1} unidades del producto {producto_1}. Nuevo stock: {nuevo_stock_2}")
    con.close()


def mostrar_dataframe(base):
    df = f'{base}.db'
    con = sqlite3.connect(df)
    cur = con.cursor()
    data_df_2 = pd.read_sql_query(f'SELECT * FROM {base}', con)
    st.dataframe(data_df_2, hide_index=True)
    con.close()


# -------------------------------------------------------------------------------------------------------------------------
# Crear la base de datos si no existe
con, cur = base_stock()
con.close()

# Crear la base de datos si no existe
con, cur = base_ventas()
con.close()

# Crear la base de datos si no existe
con, cur = base_precios()
con.close()

# -------------------------------------------------------------------------------------------------------------------------
# Configuracion del sidebar
tipo_operacion = st.sidebar.selectbox('Opción..',
                                      ['Ingresos',
                                       'Consultas'
                                       ])

if tipo_operacion == 'Consultas':
    opciones = st.sidebar.selectbox("Elija una opcion..",
                                    ["Ventas",
                                     "Productos",
                                     "Precios",
                                     "Stock",
                                     "Compras"])
else:
    opciones = st.sidebar.selectbox("Elija una opcion..",
                                    ["Ventas",
                                     "Compras",
                                     "Ingreso de mercaderia",
                                     "Precios"
                                     ])
# -----------------------------------------------------------------------------------------------------------------------------
# Formulario de ventas

    # =--=--=--=--=--=--=--=--=--=Back-end=--=--=--=--=--=--=--=--=--=
# Utilizar sesiones para mantener la información entre ejecuciones
session_state = st.session_state

if 'ventas_temporales' not in session_state:
    session_state.ventas_temporales = []

if 'df_ventas_temporales' not in session_state:
    session_state.df_ventas_temporales = pd.DataFrame(
        columns=['Producto', 'Cantidad', 'Precio', 'Subtotal', 'Status'])

# Variable para controlar si se debe finalizar
finalizar = False
total_ventas = 0
df = []

if tipo_operacion == "Ingresos" and opciones == "Ventas":
    # Crear la base de datos si no existe
    con = sqlite3.connect('stock.db')
    data_df = pd.read_sql_query('SELECT * FROM stock', con)
    con.close()

    # ==========================front-end==========================
    centrar_texto("Ingrese una venta", 3, 'white')
    col100, col101 = st.columns([4, 8])
    with col100:
        with st.form("Ventas"):
            col00, col01, col02 = st.columns([1.3, 1.7, 1.3])
            col03, col04, col05 = st.columns([1, 4, 1])
            col06, col07, col08 = st.columns([1, 4, 1])
            col09, col10, col11 = st.columns([1, 4, 1])
            col12, col13, col14 = st.columns([1, 4, 1])
            col15, col16, col17 = st.columns([1, 4, 1])
            col18, col19, col20 = st.columns([1, 4, 1])
            col21, col22, col23 = st.columns([2, 3, 2])
            col24, col25, col26 = st.columns([2, 3, 2])

            with col01:
                cantidad = st.number_input("Cantidad", min_value=1)
            with col04:
                producto = st.selectbox("Elija el producto...",
                                        data_df['producto'].sort_values())

        # =--=--=--=--=--=--=--=--=--=Back-end=--=--=--=--=--=--=--=--=--=
            # Conectar a la base de datos "stock.db"
            con_precio, cur_precio = base_precios()
            # Verificar si existe el producto
            cur_precio.execute(
                "SELECT precio_venta FROM precios WHERE producto=?", (producto,))
            result_3 = cur_precio.fetchone()
            precio_unitario = result_3[0]
            status = False
            sub_total = precio_unitario * cantidad

        # ==========================front-end==========================
            with col07:
                centrar_texto("Precio unitario", 5, 'lightblue')
            with col10:
                centrar_texto(f'R$ {precio_unitario:.2f}', 3, 'white')
            with col13:
                centrar_texto('Sub-Total', 5, 'lightblue')
            with col16:
                centrar_texto(f'R$ {sub_total:.2f}', 3, 'white')
            with col19:
                centrar_texto('Total', 5, 'lightblue')
            with col25:
                button_agregar = st.form_submit_button(
                    'Agregar', use_container_width=True)
                st.caption("")

        # =--=--=--=--=--=--=--=--=--=Back-end=--=--=--=--=--=--=--=--=--=
                if button_agregar:
                    venta_actual = {'Producto': producto, 'Cantidad': cantidad,
                                    'Precio': precio_unitario, 'Subtotal': sub_total, 'Status': status}
                    session_state.ventas_temporales.append(venta_actual)
                    session_state.df_ventas_temporales = pd.DataFrame(
                        session_state.ventas_temporales)
                    # Sumar todas las ventas
                    total_ventas = sum(venta['Subtotal']
                                       for venta in session_state.ventas_temporales)

        # ==========================front-end==========================
            with col22:
                centrar_texto(f'R$ {total_ventas:.2f}', 3, 'white')
    with col101:
        with st.form('Tabla_ventas'):
            edited_data = st.data_editor(session_state.df_ventas_temporales.tail(11), width=800, height=452, hide_index=True,
                                         column_config={
                "Producto": st.column_config.TextColumn(
                    "Producto",
                    width="medium",
                ),
                "Cantidad": st.column_config.NumberColumn(
                    "Cantidad",
                    width="small",
                ),
                "Precio": st.column_config.NumberColumn(
                    "Precio",
                    width="small",
                ),
                "Subtotal": st.column_config.NumberColumn(
                    "Subtotal",
                    width="small",
                ),
                "Status": st.column_config.CheckboxColumn(
                    "Cancelar",
                    help="Seleccione su status. Si esta tildado esta cancelado",
                    default=False,
                    width='small',
                ),
            })

            col50, col51, col52, col53, col54 = st.columns([2, 2, 5, 1, 2.7])
            with col52:
                finalizar = st.form_submit_button(
                    'Finalizar', use_container_width=True)
            # with col54:
            #    cancelar = st.form_submit_button('Cancelar producto', use_container_width=True)

        # =--=--=--=--=--=--=--=--=--=Back-end=--=--=--=--=--=--=--=--=--=
            # if cancelar:
                # Obtener los datos editados por el usuario desde el data editor
            #    for index, row in edited_data.iterrows():
            #        ventas_actuales = {'Producto': row['Producto'], 'Cantidad': row['Cantidad'], 'Precio': row['Precio'], 'Subtotal': row['Subtotal'], 'Status': row['Status']}
            #        if row["Status"] == False:
            #            df.append(ventas_actuales)
            #            df_tabla = pd.DataFrame(df)
            #        # Sumar todas las ventas
            #        total_venta = sum(venta['Subtotal'] for venta in df)
            #    print(df_tabla)
            #    print(total_venta)

            # Acciones al presionar "Finalizar"
            if finalizar:
                # Obtener los datos editados por el usuario desde el data editor
                for index, row in edited_data.iterrows():
                    ventas_actuales = {'Producto': row['Producto'], 'Cantidad': row['Cantidad'],
                                       'Precio': row['Precio'], 'Subtotal': row['Subtotal'], 'Status': row['Status']}
                    df.append(ventas_actuales)

                # Realizar las acciones de finalización
                for venta in df:
                    agregar_ventas(venta['Producto'],
                                   venta['Cantidad'], venta['Status'])
                    if not venta['Status']:
                        quitar_productos(venta['Producto'], venta['Cantidad'])

                # Reiniciar el DataFrame
                session_state.df_ventas_temporales = pd.DataFrame(
                    columns=['Producto', 'Cantidad', 'Precio', 'Subtotal', 'Status'])
                # También puedes reiniciar la lista si lo deseas
                session_state.ventas_temporales = []
                st.rerun()
                st.success("Ventas registradas y stock actualizado con éxito.")
# -----------------------------------------------------------------------------------------------------------------------------
# Ingreso de mercaderia
if tipo_operacion == "Ingresos" and opciones == "Ingreso de mercaderia":
    centrar_texto("Ingrese un producto", 3, 'white')
    radio = st.radio("Elija una opción", [
                     "***Nuevo producto***", "***Producto existente***"])
    with st.form("Ventas"):
        if radio == "***Nuevo producto***":
            producto_1 = st.text_input('Ingrese un producto..')
            cantidad_1 = st.number_input("Ingrese cantidad..", min_value=0)

        elif radio == "***Producto existente***":
            con = sqlite3.connect('stock.db')
            data_df_2 = pd.read_sql_query('SELECT * FROM stock', con)
            con.close()
            producto_1 = st.selectbox(
                "Elija el producto...", data_df_2['producto'].sort_values())
            cantidad_1 = st.number_input("Ingrese cantidad..", min_value=0)

        button_003 = st.form_submit_button('Finalizar')
        if button_003:
            if radio == "***Nuevo producto***":
                if producto_1 == "" or cantidad_1 == 0:
                    st.caption("Datos faltantes")
                else:
                    # Verificar si el producto ya tiene precio de venta
                    con_ver = sqlite3.connect('stock.db')
                    cur_ver = con_ver.cursor()
                    cur_ver.execute(
                        "SELECT producto FROM stock WHERE producto=?", (producto_1,))
                    result_3 = cur_ver.fetchone()
                    if result_3 is None:
                        agregar_productos(producto_1, cantidad_1)
                        st.caption("Producto agregado con exito!!")
                    else:
                        st.warning(
                            "El producto ya existe, seleccione 'Producto existete'", icon="⚠️")
            else:
                if producto_1 == "" or cantidad_1 == 0:
                    st.caption("Datos faltantes")
                else:
                    sumar_productos(producto_1, cantidad_1)
                    st.caption("Producto sumado con exito!!")
# -----------------------------------------------------------------------------------------------------------------------------
# Formulario de precios
if tipo_operacion == "Ingresos" and opciones == "Precios":
    centrar_texto("Precios", 3, 'white')
    radio_2 = st.radio("Elija una opción", [
        "***Nuevo precio***", "***Modificar precio***"])
    with st.form("Precios"):
        if radio_2 == "***Nuevo precio***":
            con = sqlite3.connect('stock.db')
            data_df_3 = pd.read_sql_query('SELECT * FROM stock', con)
            con.close()
            producto_2 = st.selectbox(
                "Elija el producto...", data_df_3['producto'].sort_values())

            precio_compra = st.number_input("Precio de compra", min_value=0.00)
            precio_venta = st.number_input("Precio de venta", min_value=0.00)

            button_4 = st.form_submit_button('Finalizar')
            if button_4:
                # Verificar si el producto ya tiene precio de venta
                con_ver = sqlite3.connect('precios.db')
                cur_ver = con_ver.cursor()
                cur_ver.execute(
                    "SELECT precio_venta FROM precios WHERE producto=?", (producto_2,))
                result_3 = cur_ver.fetchone()
                cur_ver.execute(
                    "SELECT precio_compra FROM precios WHERE producto=?", (producto_2,))
                result_4 = cur_ver.fetchone()
                if result_3 is None:
                    agregar_precio(producto_2, precio_compra, precio_venta)
                    st.caption("Precio agregado con exito!!")
                else:
                    precio_v_actual = result_3[0]
                    precio_c_actual = result_4[0]
                    st.warning(f"Item con precio de compra vigente de R$ {precio_c_actual}")
                    st.warning(f"Item con precio de venta vigente de R$ {precio_v_actual}")
                    st.warning(
                        "Selecciona la opcion 'Modificar precio'", icon="⚠️")
                    st.stop()

        elif radio_2 == "***Modificar precio***":
            con = sqlite3.connect('stock.db')
            data_df_3 = pd.read_sql_query('SELECT * FROM stock', con)
            con.close()
            producto_2 = st.selectbox(
                "Elija el producto...", data_df_3['producto'].sort_values())

            precio_compra = st.number_input("Precio de compra", min_value=0.00)
            precio_venta = st.number_input("Precio de venta", min_value=0.00)
            button_4 = st.form_submit_button('Finalizar')
            if button_4:
                # Verificar si el producto ya tiene precio de venta
                con_ver = sqlite3.connect('precios.db')
                cur_ver = con_ver.cursor()
                cur_ver.execute(
                    "SELECT precio_venta FROM precios WHERE producto=?", (producto_2,))
                result_3 = cur_ver.fetchone()
                # precio_actual = result_3[0]
                if result_3 is None:
                    st.warning(
                        'Esta no es la opcion para un nuevo precio', icon="⚠️")
                    st.stop()
                else:
                    modificar_precio(producto_2, precio_compra, precio_venta)
                    st.caption("Precio modificado con exito")

# -----------------------------------------------------------------------------------------------------------------------------
# Consultas
# Ventas
if tipo_operacion == "Consultas" and opciones == "Ventas":
    mostrar_dataframe('ventas')
if tipo_operacion == "Consultas" and opciones == "Productos":
    mostrar_dataframe("stock")
if tipo_operacion == "Consultas" and opciones == "Precios":
    mostrar_dataframe("precios")
if tipo_operacion == "Consultas" and opciones == "Stock":
    mostrar_dataframe("stock")
if tipo_operacion == "Consultas" and opciones == "Compras":
    mostrar_dataframe("stock")
