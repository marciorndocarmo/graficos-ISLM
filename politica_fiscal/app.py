import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide", page_title="Política Fiscal no Modelo IS-LM")

# ----------------------------------------
# Componentes da LM
# ----------------------------------------

# Controles deslizantes
st.sidebar.header("Componentes da LM")
LM_intercept = st.sidebar.number_input("LM: intercepto (a)", value=2.0, step=1.0)
LM_slope = st.sidebar.number_input("LM: inclinação da reta (b)", value=0.01, step=0.005, format="%.3f")

# ----------------------------------------
# Componentes da IS1
# ----------------------------------------

st.sidebar.header("Componentes IS1")
IS1_G = st.sidebar.number_input("IS1: G (Gastos autônomos)", value=5.0, step=1.0)
IS1_T = st.sidebar.number_input("IS1: T (Tributação)", value=10.0, step=1.0)
IS1_slope = st.sidebar.number_input("IS1: inclinação da curva", value=0.001, step=0.005, format="%.3f")

# ----------------------------------------
# Componentes da IS2
# ----------------------------------------

st.sidebar.header("Componentes IS2")
IS2_G = st.sidebar.number_input("IS2: G (Gastos autônomos)", value=5.0, step=1.0)
IS2_T = st.sidebar.number_input("IS2: T (Tributação)", value=10.0, step=1.0)
IS2_slope = st.sidebar.number_input("IS2: inclinação da curva ", value=0.001, step=0.005, format="%.3f")


st.sidebar.header("Equação da IS \n (IS = base + x*G - x*T)")
base_A = st.sidebar.number_input("base_IS", value=5.0, step=0.5)
kG = 0.25
kT = 0.25

# ----------------------------------------
# Construção das Curvas
# ----------------------------------------

Y = np.linspace(0, 1000, 500)

def LM_i(Y, a_LM, b_LM):
    return a_LM + b_LM * Y

def IS_intercept(G, T, base_A, kG, kT):
    return base_A + kG * G - kT * T

def IS_i(Y, A, d):
    return A - d * Y

# ----------------------------------------
# Cálculo dos pontos de interseção
# ----------------------------------------

A1 = IS_intercept(IS1_G, IS1_T, base_A, kG, kT)
A2 = IS_intercept(IS2_G, IS2_T, base_A, kG, kT)

LM_vals = LM_i(Y, LM_intercept, LM_slope)
IS1_vals = IS_i(Y, A1, IS1_slope)
IS2_vals = IS_i(Y, A2, IS2_slope)

# Evite plotar taxas de juros negativas substituindo valores negativos por NaN
LM_plot = np.where(LM_vals < 0, np.nan, LM_vals)
IS1_plot = np.where(IS1_vals < 0, np.nan, IS1_vals)
IS2_plot = np.where(IS2_vals < 0, np.nan, IS2_vals)

# Função auxiliar de interseção (retorna None se a taxa de interseção for menor que 0 ou se o denominador for muito pequeno)
def intersection_point(A, d, a_LM, b_LM):
    denom = (b_LM + d)
    if abs(denom) < 1e-12:
        return None
    Y_star = (A - a_LM) / denom
    i_star = LM_i(Y_star, a_LM, b_LM)
    # Se a interseção implicar em taxa de juros negativa, considere que não há interseção viável sob a condição i ≥ 0.
    if i_star < 0:
        return None
    return (Y_star, i_star)

pt1 = intersection_point(A1, IS1_slope, LM_intercept, LM_slope)
pt2 = intersection_point(A2, IS2_slope, LM_intercept, LM_slope)

# Para definir o intervalo de exibição, calcule o maior valor positivo de i entre os valores plotados; se não houver, use 1.0 como valor padrão
max_i_candidates = []
for arr in [LM_plot, IS1_plot, IS2_plot]:
    if np.isfinite(arr).any():
        max_i_candidates.append(np.nanmax(arr))
max_i = max(max_i_candidates) if max_i_candidates else 1.0
yaxis_max = max(1.0, max_i * 1.15)

# ----------------------------------------
# Gráfico
# ----------------------------------------

fig = go.Figure()

# Legenda
fig.add_trace(go.Scatter(x=Y, y=LM_plot, mode="lines", name="LM", line=dict(width=3, color="green")))
fig.add_trace(go.Scatter(x=Y, y=IS1_plot, mode="lines", name="IS1", line=dict(width=3, color="red")))
fig.add_trace(go.Scatter(x=Y, y=IS2_plot, mode="lines", name="IS2", line=dict(width=3, color="orange")))

# Adicione marcadores de interseção apenas se a interseção existir e tiver i ≥ 0
if pt1 is not None and 0 <= pt1[0] <= 1000:
    fig.add_trace(go.Scatter(x=[pt1[0]], y=[pt1[1]], mode="markers+text", name="Equilíbrio IS1/LM",
                             marker=dict(size=10, color="white"), text=[], textposition="top center"))
if pt2 is not None and 0 <= pt2[0] <= 1000:
    fig.add_trace(go.Scatter(x=[pt2[0]], y=[pt2[1]], mode="markers+text", name="Equilíbrio IS2/LM",
                             marker=dict(size=10, color="white"), text=[], textposition="bottom center"))

# Linhas pontilhadas nos pontos de equilíbrio
for Y_eq, i_eq, color in [(pt1[0], pt1[1], 'white'), (pt2[0], pt2[1], 'white')]:
    # Linha vertical até o eixo x
    fig.add_trace(go.Scatter(
        x=[Y_eq, Y_eq],
        y=[0, i_eq],
        mode="lines",
        line=dict(color=color, width=1, dash="dot"),
        showlegend=False
    ))
    # Linha horizontal até o eixo y
    fig.add_trace(go.Scatter(
        x=[0, Y_eq],
        y=[i_eq, i_eq],
        mode="lines",
        line=dict(color=color, width=1, dash="dot"),
        showlegend=False
    ))


# Se as interseções forem inviáveis porque implicam i < 0, mostre marcadores no piso vinculante i = 0, onde cada curva cruza i = 0 (se estiver dentro do intervalo de Y)
def Y_where_LM_equals_i0(a_LM, b_LM):
    # Solve a + bY = 0 --> Y = -a / b
    if abs(b_LM) < 1e-12:
        return None
    return -a_LM / b_LM

def Y_where_IS_equals_i0(A, d):
    # Solve A - dY = 0 --> Y = A / d
    if abs(d) < 1e-12:
        return None
    return A / d

# Mostre os marcadores do piso vinculante apenas se as interseções reais estiverem ausentes.
if pt1 is None:
    ylm0 = Y_where_LM_equals_i0(LM_intercept, LM_slope)
    yis10 = Y_where_IS_equals_i0(A1, IS1_slope)
    # Plote marcadores em r = 0 se estiverem dentro do domínio
    markers = []
    if ylm0 is not None and 0 <= ylm0 <= 1000:
        markers.append(("LM @ i=0", ylm0))
    if yis10 is not None and 0 <= yis10 <= 1000:
        markers.append(("IS1 @ i=0", yis10))
    for name, yv in markers:
        fig.add_trace(go.Scatter(x=[yv], y=[0], mode="markers+text", name=name,
                                 marker=dict(size=8, symbol="diamond"), text=[f"{name}\nY={yv:.1f}"], textposition="top center"))

if pt2 is None:
    ylm0 = Y_where_LM_equals_i0(LM_intercept, LM_slope)
    yis20 = Y_where_IS_equals_i0(A2, IS2_slope)
    markers = []
    if ylm0 is not None and 0 <= ylm0 <= 1000:
        markers.append(("LM @ i=0", ylm0))
    if yis20 is not None and 0 <= yis20 <= 1000:
        markers.append(("IS2 @ i=0", yis20))
    for name, yv in markers:
        fig.add_trace(go.Scatter(x=[yv], y=[0], mode="markers+text", name=name,
                                 marker=dict(size=8, symbol="diamond"), text=[f"{name}\nY={yv:.1f}"], textposition="bottom center"))

fig.update_layout(
    title="Modelo IS-LM: Interatividade com Política Fiscal ",
    xaxis_title="Produto (Y)",
    yaxis_title="Taxa de juros (r)",
    yaxis=dict(range=[0, 10]),  # fixa r entre 0 e 10
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    
)

st.plotly_chart(fig, use_container_width=True)

# Mostre os valores numéricos em blocos
col1, col2, col3 = st.columns(3)
with col1:
    
    if pt1:
        st.success(f"IS1  Y: {pt1[0]:.2f} | r: {pt1[1]:.2f}")
    else:
        st.warning("Equilíbrio IS1/LM implica i < 0 — restrito a i = 0 no gráfico. Marcadores mostram onde cada curva cruza i = 0 (se estiver no domínio).")

with col2:
    
    if pt2:
        st.success(f"IS2  Y: {pt2[0]:.2f} | r: {pt2[1]:.2f}")
    else:
        st.warning("Equilíbrio IS2/LM implica i < 0 — restrito a i = 0 no gráfico. Marcadores mostram onde cada curva cruza i = 0 (se estiver no domínio).")

with col3:
    
    if pt2:
        st.success(f" $\Delta$ Y: {pt2[0]-pt1[0]:.2f}  $\Delta$ r: {pt2[1]-pt1[1]:.2f}")
    else:
        st.warning("Equilíbrio IS2/LM implica i < 0 — restrito a i = 0 no gráfico. Marcadores mostram onde cada curva cruza i = 0 (se estiver no domínio).")

# Nota de Explicação
st.markdown("""
Este simulador mostra o efeito da Política Fiscal no equilíbrio entre o mercado de bens (IS) e o mercado monetário (LM).
Use os controles para alterar os componentes e observar como muda o equilíbrio.
""")
