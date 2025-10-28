import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide", page_title="Política Monetária no Modelo IS-LM")

# ----------------------------------------
# Componentes da IS
# ----------------------------------------
st.sidebar.header("Componentes da Curva IS")
is_slope = st.sidebar.number_input("Inclinação da IS (em módulo)", value=0.002, step=0.001, format="%.3f")
is_intercept = st.sidebar.number_input("Intercepto da IS", value=5.0, step=0.1, format="%.2f")

# ----------------------------------------
# Componentes da LM1
# ----------------------------------------
st.sidebar.header("Componentes da Curva LM1")
lm1_money = st.sidebar.number_input("Oferta de moeda (LM1)", value=2.0, step=0.1, format="%.2f")
lm1_slope = st.sidebar.number_input("Inclinação da LM1", value=0.01, step=0.001, format="%.3f")

# ----------------------------------------
# Componentes da LM2
# ----------------------------------------
st.sidebar.header("Componentes da Curva LM2")
lm2_money = st.sidebar.number_input("Oferta de moeda (LM2)", value=2.0, step=0.1, format="%.2f")
lm2_slope = st.sidebar.number_input("Inclinação da LM2", value=0.01, step=0.001, format="%.3f")

# ----------------------------------------
# Construção das curvas
# ----------------------------------------
Y = np.linspace(0, 1000, 500)

# Curva IS
i_IS = is_intercept - is_slope * Y

# Curvas LM
i_LM1 = (5-lm1_money) + lm1_slope * Y
i_LM2 = (5-lm2_money) + lm2_slope * Y

# Limites do gráfico
y_min, y_max = 2, 8

# ----------------------------------------
# Cálculo dos pontos de interseção
# ----------------------------------------
def find_intersection(y_vals, i1, i2):
    diff = np.abs(i1 - i2)
    idx = np.argmin(diff)
    return y_vals[idx], i1[idx]

Y_eq1, i_eq1 = find_intersection(Y, i_IS, i_LM1)
Y_eq2, i_eq2 = find_intersection(Y, i_IS, i_LM2)

# ----------------------------------------
# Ponto móvel na LM2
# ----------------------------------------

# Encontrar Y correspondente à taxa de juros escolhida
Y_ini = Y_eq1

# encontrar o i correspondente

i_moving_default =(5-lm2_money) + lm2_slope * Y_ini

interest_increment = st.sidebar.number_input("Taxa de juros (ponto na LM2)", value=0.00, step=0.05, format="%.2f")

interest_point = i_moving_default + interest_increment

Y_moving = (interest_point -(5-lm2_money)) / lm2_slope



# ----------------------------------------
# Gráfico
# ----------------------------------------
fig = go.Figure()

# Legenda
fig.add_trace(go.Scatter(x=Y, y=i_IS, mode='lines', name='Curva IS', line=dict(color='red', width=3)))
fig.add_trace(go.Scatter(x=Y, y=i_LM1, mode='lines', name='Curva LM1', line=dict(color='green', width=3)))
fig.add_trace(go.Scatter(x=Y, y=i_LM2, mode='lines', name='Curva LM2', line=dict(color='orange', width=3)))

# Pontos de interseção
fig.add_trace(go.Scatter(x=[Y_eq1], y=[i_eq1], mode='markers', marker=dict(size=10, color='white'), name='Equilíbrio LM1'))
fig.add_trace(go.Scatter(x=[Y_eq2], y=[i_eq2], mode='markers', marker=dict(size=10, color='white'), name='Equilíbrio LM2'))

# Linhas pontilhadas nos equilíbrios
for Y_eq, i_eq, color in [(Y_eq1, i_eq1, 'white'), (Y_eq2, i_eq2, 'white')]:
    fig.add_trace(go.Scatter(x=[Y_eq, Y_eq], y=[2, i_eq], mode='lines',
                             line=dict(color=color, width=1, dash='dot'), showlegend=False))
    fig.add_trace(go.Scatter(x=[0, Y_eq], y=[i_eq, i_eq], mode='lines',
                             line=dict(color=color, width=1, dash='dot'), showlegend=False))

# Ponto móvel sobre LM2
if Y_moving:
    fig.add_trace(go.Scatter(x=[Y_moving], y=[interest_point],
                             mode='markers', marker=dict(size=12, color='red'),
                             name='Ponto móvel LM2'))

# Configuração dos eixos
fig.update_layout(
    title="Modelo IS-LM: Interatividade com Política Monetária",
    xaxis_title="Produto (Y)",
    yaxis_title="Taxa de Juros (r)",
    xaxis=dict(range=[0, 1000]),
    yaxis=dict(range=[y_min, y_max]),
    template="plotly_white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

# Exibir o gráfico
st.plotly_chart(fig, use_container_width=True)

# Mostre os valores numéricos em blocos
col1, col2, col3, col4 = st.columns(4)

with col1:    
    st.success(f"LM1  Y: {Y_eq1:.2f} | r: {i_eq1:.2f}")
   
with col2:    
    st.success(f"LM2  Y: {Y_eq2:.2f} | r: {i_eq2:.2f}")
    
with col3:    
    st.success(f" $\Delta$ Y: {Y_eq2 - Y_eq1:.2f}  $\Delta$ r: {i_eq2 - i_eq1:.2f}")
    
with col4:    
    st.success(f"PM Y: {Y_moving:.2f} r: {interest_point:.2f}")
   
# Nota de Explicação
st.markdown("""
Este simulador mostra o efeito da política monetária no equilíbrio entre o mercado de bens (IS) e o mercado monetário (LM).
Use os controles para alterar os componentes e observar como muda o equilíbrio.
""")

