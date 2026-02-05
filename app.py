import streamlit as st
import math

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Calculadora ADT", page_icon="💧")

# --- ESTILOS ---
st.markdown("""
    <style>
    .stButton>button {
        background-color: #d32f2f;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        width: 100%;
        height: 3.5em;
    }
    .main { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO ---
try:
    st.image("LOGO PRINCIPAL.png", width=220)
except:
    st.markdown("<h1 style='color: #d32f2f;'>TOMOCORP</h1>", unsafe_allow_html=True)

st.subheader("Ingeniería de Innovación - Hans Longa")

# --- LÓGICA MATEMÁTICA ---
def obtener_viscosidad(temp):
    datos_visco = {0: 0.001792, 10: 0.001308, 20: 0.001003, 30: 0.000798, 40: 0.000653, 
                   50: 0.000547, 60: 0.000467, 70: 0.000404, 80: 0.000355, 90: 0.000315, 100: 0.000282}
    t_base = (temp // 10) * 10
    if t_base >= 100: return datos_visco[100]
    v1, v2 = datos_visco[t_base], datos_visco[t_base + 10]
    return v1 + (v2 - v1) * (temp - t_base) / 10

def calcular_friccion_colebrook(re, rugosidad_relativa):
    if re < 2300: return 64 / re
    f = 0.02
    for _ in range(15): # Aumentado a 15 iteraciones para mayor precisión
        f = 1 / (-2 * math.log10((rugosidad_relativa / 3.7) + (2.51 / (re * math.sqrt(f)))))**2
    return f

# --- INTERFAZ ---
with st.form("calculadora_adt"):
    st.markdown("### 1. Datos de la Tubería")
    col1, col2 = st.columns(2)
    
    with col1:
        q_val = st.number_input("Caudal", min_value=0.0, value=10.0, step=0.1)
        u_q = st.selectbox("Unidad Caudal", ["L/s", "m³/h"])
        d_ext = st.number_input("Diámetro Exterior", min_value=0.1, value=110.0)
        u_d = st.selectbox("Unidad Diámetro", ["mm", "Pulgadas"])

    with col2:
        espesor = st.number_input("Espesor de Pared", min_value=0.0, value=6.3)
        u_e = st.selectbox("Unidad Espesor", ["mm", "Pulgadas"])
        temp = st.slider("Temperatura del Agua (°C)", 0, 100, 20)
        material = st.radio("Material", ["HDPE", "Acero"], horizontal=True)

    st.markdown("### 2. Instalación")
    longitud = st.number_input("Longitud Total Tubería (m)", min_value=0.1, value=100.0)
    cota = st.number_input("Altura Geométrica / Cota (m)", value=10.0)
    valvula = st.checkbox("Incluir Válvula Check (K=2.5)")

    submit = st.form_submit_button("CALCULAR ADT")

# --- PROCESAMIENTO ---
if submit:
    # Conversiones a Sistema Internacional (m, m3/s)
    caudal_ms = q_val / 1000 if u_q == "L/s" else q_val / 3600
    
    # Normalización de Diámetro y Espesor
    d_ext_m = d_ext * 0.001 if u_d == "mm" else d_ext * 0.0254
    e_m = espesor * 0.001 if u_e == "mm" else espesor * 0.0254
    
    d_int_m = d_ext_m - (2 * e_m) # Diámetro interno real

    if d_int_m <= 0:
        st.error("❌ Error: El espesor es mayor que el radio de la tubería.")
    else:
        # Rugosidad absoluta
        k = 0.00008 if material == "HDPE" else 0.00015
        
        # Hidráulica
        area = (math.pi * d_int_m**2) / 4
        vel = caudal_ms / area
        visco_dinamica = obtener_viscosidad(temp)
        # Aproximación de densidad del agua a 1000 kg/m3 para Reynolds
        re = (vel * d_int_m * 1000) / visco_dinamica
        
        f = calcular_friccion_colebrook(re, k / d_int_m)
        g = 9.81
        
        # Pérdidas
        hf = f * (longitud / d_int_m) * (vel**2 / (2 * g))
        hm = 2.5 * (vel**2 / (2 * g)) if valvula else 0
        adt_final = cota + hf + hm

        # Resultados
        st.success(f"## ADT: {adt_final:.2f} m.c.a.")
        
        # Auditoría de datos para el Ingeniero
        with st.expander("Ver variables de control"):
            st.write(f"**Diámetro Interno:** {d_int_m*1000:.2f} mm")
            st.write(f"**Velocidad de flujo:** {vel:.2f} m/s")
            st.write(f"**N° Reynolds:** {re:.0f}")
            st.write(f"**Factor de fricción (f):** {f:.4f}")

st.markdown("---")
st.caption("Aplicativo desarrollado por el Ing. Hans Longa")