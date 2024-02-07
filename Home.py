import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='🏠'
)

# image_path = '\\Users\\joaom\\OneDrive\\repos\\comunidade_DS\\exercicio_data_frames\\img\\port2.jpg'
Image = Image.open('logo.png')
st.sidebar.image(Image, width=120)

st.sidebar.markdown('# MTZ delivers')
st.sidebar.markdown('## Best delivery from Matozinhos')
st.sidebar.markdown("""___""")

st.write('# MTZ Delivers Dashboard')

st.markdown(
    """
        MTZ Delivers dashboard foi construido para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
        ### Como utilizar o dashboard?
        - Visão Empresa:
          - Visão Gerencial: Métricas gerais de comportamento.
          - Visão Tática: Indicadores semanais de crescimento.
          - Visão Geográfica: Insights de geolocalização.
        - Visão Entregador:
          - Acompanhamento os indicadores semanais de crescimento
        - Visão Restaurantes:
          - Indicadores semanais de crescimento dos restaurantes
          
        ## Ask for Help
        - João Marcos
        - @jtercio on instagram
    """    )