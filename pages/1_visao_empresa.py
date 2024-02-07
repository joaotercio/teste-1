######################################
# IMPORTANDO AS BIBLIOTECAS
#####################################

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static
from datetime import datetime, timedelta

st.set_page_config(page_title='Visão Empresa', page_icon='📊', layout='wide')

##########################################
# FUNÇÕES
##########################################
def clean_code(df1):
    """ Esta função tem a responsabildaide de limpar o dataframe
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. formatação da coluna de datas
        5 Limpeza da coluna de tempo (remoção do texto da variável numérica)

        Input: Dataframe
        Output: Dataframe
    """
    #removendo os espaços dentro de strings/texto/object
    df1.loc[:,'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[:,'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:,'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:,'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:,'City'] = df1.loc[:,'City'].str.strip()
    df1.loc[:,'Festival'] = df1.loc[:,'Festival'].str.strip()

    #1. convertendo a coluna Age de texto para numero 
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1 ['Delivery_person_Age'] = df1 ['Delivery_person_Age'].astype(int)

    #2. convertendo a coluna Ratings de texto para numero decimal (float)
    df1 ['Delivery_person_Ratings'] = df1 ['Delivery_person_Ratings'].astype( float )

    #3. convertendo a coluna order_date de texto para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    #4. convertendo multiple_deliveries de texto para numero inteiro (int)
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1 ['mmultiple_deliveries'] = df1 ['multiple_deliveries'].astype(int)

    #5. removendo NaN de weatherconditions

    linhas_selecionadas = (df1['Weatherconditions'] != 'conditions NaN')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    #6. removendo NaN de road_traffic_conditions

    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    #6. removendo NaN de City

    linhas_selecionadas = (df1['City'] != 'NaN')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    #7. Limpando coluna de time taken

    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1
#----------------------------------------------------------------------------------------------------------------------------
def order_metric(df1):
    """ Esta função tem a responsabilidade de criar um gráfico de colunas dos pedidos diários
        Input: Dataframe
        Output: Column Graph
    """
    cols = ['ID', 'Order_Date']
            #seleção das linhas
    df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()
            
            #desenhar gráfico de linhas
    fig = px.bar(df_aux, x='Order_Date', y = 'ID')

    return fig
#----------------------------------------------------------------------------------------------------------------------------
def traffic_order_share(df1):
    """ Esta função tem a responsabilidade de criar um gráfico de pizza dos pedidos pedidos
        por tipo de trafégo 
        Input: Dataframe
        Output: Pie Graph
    """
    df_aux = (df1.loc[:, ['ID', 'Road_traffic_density']]
                 .groupby('Road_traffic_density')
                 .count()
                 .reset_index())
                
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
    fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')

    return fig
#----------------------------------------------------------------------------------------------------------------------------
def traffic_order_city(df1):
    """ Esta função tem a responsabilidade de criar um gráfico de bolhas dos pedidos
        por tipo de trafégo e cidade
        Input: Dataframe
        Output: Bubble Graph
    """
    df_aux = (df1.loc[:, ['ID', 'City', 'Road_traffic_density']]
                 .groupby(['City', 'Road_traffic_density'])
                 .count()
                 .reset_index())
    fig = px.scatter(df_aux, x='City', y= 'Road_traffic_density', size='ID', color='City')

    return fig
#----------------------------------------------------------------------------------------------------------------------------
def order_by_week(df1):
    """ Esta função tem a responsabilidade de criar um gráfico de linhas do número de pedidos
        por semana
        Input: Dataframe
        Output: Line Graph
    """
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux = df1.loc[:,['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line(df_aux, x='week_of_year', y = 'ID')

    return fig
#----------------------------------------------------------------------------------------------------------------------------
def order_share_by_week(df1):

    """ Esta função tem a responsabilidade de criar um gráfico de linhas do número de pedidos
        realizado por entregadores únicos por semana
        Input: Dataframe
        Output: Line Graph
    """
    df_aux1 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux2 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
    df_aux = pd.merge(df_aux1, df_aux2, how='inner')
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x='week_of_year', y='order_by_delivery')

    return fig
#----------------------------------------------------------------------------------------------------------------------------
def country_maps(df1):

    """ Esta função tem a responsabilidade de criar um gráfico de linhas do número de pedidos
        por semana
        Input: Dataframe
        Output: Map with points of interest
    """
    df_aux = (df1.loc[:,['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']]
                 .groupby(['City', 'Road_traffic_density'])
                 .median()
                 .reset_index())
        
    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup=location_info[['City','Road_traffic_density' ]]).add_to(map)
    folium_static (map, width=1024, height=600)

    return None

##########################################
# IMPORTANDO DATASET E REALIZANDO LIMPEZA DOS DADOS
##########################################
df = pd.read_csv('train.csv')
df1 = df.copy()
#limpeza dos dados
df1 = clean_code(df)

######################################
# CONSTRUINDO LAYOUT NO STREAMLIT
#####################################

######################################
# BARRA LATERAL
#####################################
st.header('Visão Empresa')
#sidebar
#image_path = '\\Users\\joaom\\OneDrive\\repos\\comunidade_DS\\exercicio_data_frames\\img\\port2.jpg'
Image = Image.open('logo.png')
st.sidebar.image(Image, width=120)

st.sidebar.markdown('# MTZ delivers')
st.sidebar.markdown('## Best delivery from Matozinhos')
st.sidebar.markdown("""___""")

#---------------------------
#  FILTROS DA BARRA LATERAL
#---------------------------
#filtro de data 
start_date = datetime(2022, 2, 11)
end_date = start_date + timedelta(days=54)
 
date_slider = st.sidebar.slider(
    "Select a date range",
    min_value=start_date,
    max_value=end_date,
    value=(start_date))

st.sidebar.markdown("""---""")
#filtro para escolher o tipo de trafego
traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('## Desenvolvido por João Marcos')

#filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas,:]

#filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options) 
df1 = df1.loc[linhas_selecionadas,:]

######################################
# ABA DAS VISÕES
####################################

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])

with tab1:
    with st.container():
        fig = order_metric(df1)
        st.markdown('# Orders by day')
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            fig = traffic_order_share(df1)
            st.markdown('### Orders by traffic')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = traffic_order_city(df1)
            st.markdown('### Orders by traffic and City')
            st.plotly_chart(fig, use_container_width=True)
                
with tab2:
    with st.container():
        st.markdown('### Orders by Week')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown('### Order Share by Week')
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown('# Country Maps')
    country_maps(df1)

    
