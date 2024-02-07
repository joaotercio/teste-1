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
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title='Visão Restaurantes', page_icon='🍔', layout='wide')

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
#--------------------------------------------------------------------------------------------------------------------
def haversine_distance (df1,fig):
    
    if fig == False:
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude',
                'Restaurant_latitude', 'Restaurant_longitude']

        df1['distance'] = (df1.loc[:, cols].apply(lambda x:
                                haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                    (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1))
                
        avg_distance =np.round(df1['distance'].mean(),2)

        return avg_distance
    
    else:
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude',
                'Restaurant_latitude', 'Restaurant_longitude']

        df1['distance'] = (df1.loc[:, cols].apply(lambda x:
                                haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                    (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1))
                
        avg_distance =df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])

        return fig


#--------------------------------------------------------------------------------------------------------------------

def avg_std_time_delivery (df1, festival, op ):
    """
                    Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
                    Parâmetros:
                         Input: 
                            - df: Dataframe com os dados necessários para o cálculo
                            - op: Tipo de opração que precisa ser calculado
                                'avg_time': calcula o tempo médio
                                'std_time': calcula o desvio padrão
                            -festival: Escolhe se tem festival ou não
                                'Yes': faz o cálculo com base no festival ativo
                                'No': faz o cálculo com bse no festival não ativo
                         Output:
                            - df: Dataframe com duas colunas e uma linha
                
    """
    df_aux = (df1.loc[:,['Time_taken(min)', 'Festival']]
                                    .groupby('Festival')
                                    .agg(['mean', 'std']))

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival,op],2)

    return df_aux

#------------------------------------------------------------------------------------------------------------------
def avg_std_time_graph (df1):
    #grafico de barras
    df_aux = df1.loc[:,['Time_taken(min)', 'City']].groupby('City').agg(['mean', 'std'])
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',
                        x=df_aux['City'],
                        y=df_aux['avg_time'],
                        error_y=dict(type='data', array=df_aux['std_time'])))
    fig.update_layout(barmode='group')
            
    return fig
#----------------------------------------------------------------------------------------------------------------------
def avg_std_traffic_density_graph(df1):
    #grafico sun
    df_aux = (df1.loc[:,['Time_taken(min)', 'City', 'Road_traffic_density']]
                            .groupby(['City','Road_traffic_density'])
                            .agg(['mean', 'std']))
                
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                                color='std_time', color_continuous_scale='RdBu',
                                color_continuous_midpoint=np.average(df_aux['std_time']))
                
    return fig
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

#-----------------------------------
# BARRA LATERAL
#-----------------------------------
st.header('VISÃO RESTAURANTES')
#sidebar
#image_path = '\\Users\\joaom\\OneDrive\\repos\\comunidade_DS\\exercicio_data_frames\\img\\port2.jpg'
Image = Image.open('logo.png')
st.sidebar.image(Image, width=120)

st.sidebar.markdown('# VISÃO RESTAURANTES')
st.sidebar.markdown('# MTZ delivers')
st.sidebar.markdown('## Best delivery from Matozinhos')
st.sidebar.markdown("""___""")

#filtro de data 
start_date = datetime(2022, 2, 13)
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
        st.title('Indicadores dos entregadores')

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            delivery_unique = (len(df1.loc[:, 'Delivery_person_ID'].unique()))
            col1.metric ('Entregadores únicos', delivery_unique)

        with col2:
            avg_distance = haversine_distance(df1, fig=False)
            col2.metric('A distancia media', avg_distance)
            
        with col3:
            df_aux = avg_std_time_delivery(df1, 'Yes', 'avg_time')
            col3.metric ('Tempo Médio de Entrega c/ Festival', df_aux)
            
        with col4:
            df_aux = avg_std_time_delivery(df1,'Yes', 'std_time')
            col4.metric ('Desvio Padrão c/ Festival', df_aux)

        with col5:
            df_aux = avg_std_time_delivery(df1, 'No', 'avg_time')
            col5.metric ('Tempo Médio de Entrega s/ Festival', df_aux)
            
        
        with col6:
            df_aux = avg_std_time_delivery(df1, 'No', 'std_time')
            col6.metric ('Desvio Padrão s/ Festival', df_aux)

    with st.container():
        st.markdown("""---""")

        fig = avg_std_time_graph(df1)
        st.plotly_chart(fig)

    with st.container():
        #st.markdown("""---""")
        st.title('Graficos pizza')

        col1, col2 = st.columns(2, gap='small')

        with col1:
            fig = haversine_distance(df1, fig=True)
            st.plotly_chart(fig)
        
        with col2:
            fig = avg_std_traffic_density_graph(df1)
            st.plotly_chart(fig)




    with st.container():
        st.markdown("""---""")
        st.title('Overall Metrics')
        df_aux = (df1.loc[:,['Time_taken(min)', 'City', 'Type_of_order']]
                     .groupby(['City','Type_of_order'])
                     .agg(['mean', 'std']))

        df_aux.columns = ['avg_time_by_order', 'std_time_by_order']
        df_aux = df_aux.reset_index()
        st.dataframe(df_aux)