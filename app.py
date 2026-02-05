import streamlit as st
import math

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Calculadora ADT - Tomocorp", page_icon="💧")

# --- ESTILOS PARA MÓVIL (Color Rojo Tomocorp) ---
st.markdown("""
    <style>
    .stButton>button {
        background-color: #d32f2f;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        width: 100%;
        height: 3em;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #d32f2f;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURACIÓN DE LOGO (Modo Web) ---
# En Streamlit, si el archivo está en la misma carpeta de GitHub, se carga así:
NOMBRE_IMAGEN = "LOGO PRINCIPAL.png"

try:
    st.image(NOMBRE_IMAGEN, width=200)
except:
    # Si la imagen no está disponible, muestra el texto con estilo
    st.markdown(f"<h1 style='color: #d32f2f;'>TOMOCORP</h1>", unsafe_allow_html=True)

st.subheader("By Ing. Hans Longa")

# --- LÓGICA DE CÁLCULO (Tu motor matemático original) ---
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
    for _ in range(10):
        f = 1 / (-2 * math.log10((rugosidad_relativa / 3.7) + (2.51 / (re * math.sqrt(f)))))**2
    return f

# --- INTERFAZ DE USUARIO (Inputs) ---
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        q_val = st.number_input("Caudal de Diseño", min_value=0.0, value=10.0)
        combo_q = st.selectbox("Unidad", ["L/s", "m³/h"])
        
        d_val = st.number_input("Diámetro Exterior", min_value=0.1, value=110.0)
        combo_d = st.selectbox("Unidad Diám.", ["mm", "Pulgadas"])

    with col2:
        e_val = st.number_input("Espesor de Pared", min_value=0.0, value=6.3)
        combo_e = st.selectbox("Unidad Esp.", ["mm", "Pulgadas"])
        
        temp = st.number_input("Temp. Agua (°C)", min_value=0.0, max_value=100.0, value=20.0)

    longitud = st.number_input("Longitud de Tubería (m)", min_value=0.1, value=100.0)
    cota = st.number_input("Elevación / Cota (m)", value=10.0)
    
    material = st.selectbox("Material:", ["HDPE", "Acero"])
    check_var = st.checkbox("Válvula Check (K=2.5)")

# --- BOTÓN DE CÁLCULO ---
if st.button("CALCULAR ADT"):
    try:
        # Conversiones
        caudal = q_val / 1000 if combo_q == "L/s" else q_val / 3600
        f_d = 0.001 if combo_d == "mm" else 0.0254
        f_e = 0.001 if combo_e == "mm" else 0.0254
        
        diam_int = (d_val * f_d) - (2 * e_val * f_e)
        
        if diam_int <= 0:
            st.error("Dato Inválido: El espesor es demasiado grande para este diámetro.")
        else:
            # Rugosidad
            rugosidad_abs = 0.00008 if material == "HDPE" else 0.00015 
            
            # Hidráulica
            visco_cin = obtener_viscosidad(temp) / 1000 
            area = (math.pi * diam_int**2) / 4
            vel = caudal / area
            re = (vel * diam_int) / visco_cin
            
            f = calcular_friccion_colebrook(re, rugosidad_abs / diam_int)
            g = 9.81
            per_friccion = f * (longitud / diam_int) * (vel**2 / (2 * g))
            per_valvula = 2.5 * (vel**2 / (2 * g)) if check_var else 0
            
            adt = cota + per_friccion + per_valvula
            
            # Resultado llamativo
            st.metric(label="ALTURA DINÁMICA TOTAL", value=f"{adt:.2f} m.c.a.")
            st.balloons()
            
    except Exception as e:
        st.error(f"Error en el ingreso de datos. Use punto para decimales.")

st.markdown("---")
st.caption("App desarrollada por Ing. Hans Longa")