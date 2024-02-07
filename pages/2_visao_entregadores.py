######################################
# BIBLIOTECAS
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

st.set_page_config(page_title='Visão Entregadores', page_icon='🛵', layout='wide')
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

#--------------------------------------------------------------------------------------------------
def top_delivers (df1, top_asc):

    df2 = (df1.loc[:, ['Time_taken(min)', 'City', 'Delivery_person_ID']]
                            .groupby(['City','Delivery_person_ID'])
                            .max()
                            .sort_values(['Time_taken(min)', 'City'], ascending=top_asc)
                            .reset_index()) 

    df_aux01 = df2.loc[df2['City'] == 'Metropolitian',:].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban',:].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban',:].head(10)

    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)

    return df3

##########################################
# IMPORTANDO DATASET E REALIZANDO LIMPEZA DOS DADOS
##########################################
df = pd.read_csv('train.csv')
df1 = df.copy()
#limpeza dos dados
df1 = clean_code(df)

######################################
# STREAMLIT
#####################################

######################################
# BARRA LATERAL
#####################################
st.header('VISÃO ENTREGADORES')
#sidebar
#image_path = '\\Users\\joaom\\OneDrive\\repos\\comunidade_DS\\exercicio_data_frames\\img\\port2.jpg'
Image = Image.open('logo.png')
st.sidebar.image(Image, width=120)

st.sidebar.markdown('# VISÃO ENTREGADORES')
st.sidebar.markdown('# MTZ delivers')
st.sidebar.markdown('## Best delivery from Matozinhos')
st.sidebar.markdown("""___""")

#filtro de data 
start_date = datetime(2022, 2, 11)
end_date = start_date + timedelta(days=54)
 
date_slider = st.sidebar.slider(
    "Selecione um periodo",
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

#filtro para escolher o tipo de clima
climatics_options = st.sidebar.multiselect(
    'Quais as condições de clima?',
    ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'],
    default=['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('## Desenvolvido por João Marcos')

#filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas,:]

#filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options) 
df1 = df1.loc[linhas_selecionadas,:]

#filtro de clima
linhas_selecionadas = df1['Weatherconditions'].isin(climatics_options) 
df1 = df1.loc[linhas_selecionadas,:]

######################################
# LAYOUT
##################################### 

tab1, tab2, ta3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')

        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            maior_idade = (df1.loc[:,'Delivery_person_Age'].max())
            col1.metric ('Maior idade', maior_idade)
            
        with col2:
            menor_idade = (df1.loc[:,'Delivery_person_Age'].min())
            col2.metric ('Menor idade', menor_idade)

        with col3:
            melhor_condicao = (df1.loc[:,'Vehicle_condition'].max())
            col3.metric ('Melhor condição', melhor_condicao)

        with col4:
            pior_condicao = (df1.loc[:,'Vehicle_condition'].min())
            col4.metric ('Pior condição', pior_condicao)


    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')

        col1, col2 = st.columns(2)
        with col1:
            st.subheader ('Avaliação média por entregador')
            df_deliver_avg = (df1.loc[:,['Delivery_person_Ratings', 'Delivery_person_ID']]
                                 .groupby('Delivery_person_ID')
                                 .mean()
                                 .reset_index())
            
            st.dataframe(df_deliver_avg)
        with col2:
            st.subheader ('Avaliação média por trânsito')
            df_deliver_avg_std_rating_by_traffic = (df1.loc[:,['Delivery_person_Ratings', 'Road_traffic_density']]
                                                       .groupby('Road_traffic_density')
                                                       .agg(['mean', 'std']))

            df_deliver_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']
            df_deliver_avg_std_rating_by_traffic = df_deliver_avg_std_rating_by_traffic.reset_index()

            st.dataframe(df_deliver_avg_std_rating_by_traffic)

            st.subheader ('Avaliação média por clima')

            df_deliver_avg_std_rating_by_weatherconditions = (df1.loc[:,['Delivery_person_Ratings', 'Weatherconditions']]
                                                                 .groupby('Weatherconditions')
                                                                 .agg(['mean', 'std']))


            df_deliver_avg_std_rating_by_weatherconditions.columns = ['delivery_mean', 'delivery_std']
            df_deliver_avg_std_rating_by_weatherconditions = df_deliver_avg_std_rating_by_weatherconditions.reset_index()

            st.dataframe(df_deliver_avg_std_rating_by_weatherconditions)

    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de Entrega')

        col1, col2 = st.columns(2)
        with col1:
            st.markdown ('##### Entregadores mais rápidos')
            df3 = top_delivers(df1, top_asc=True)
            st.dataframe(df3)

        with col2:
            st.markdown ('##### Entregadores mais lentos')
            df3 = top_delivers(df1, top_asc=False)
            st.dataframe(df3)