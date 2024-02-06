# importando todas as bibliotecas
#
# - 1º pacotes nativos do python: json, os, etc.;
import json
import geopy
from geopy.geocoders import Nominatim

# - 2º pacotes de terceiros: pandas, seabornm etc.;
import pandas as pd
import seaborn
import numpy as np
import geopandas
import matplotlib.pyplot as plt
# - 3º pacotes que você desenvolveu.

# Abrindo arquivo tabela-deliveries em DF

deliveries_df = pd.read_csv('tabela-deliveries.csv')

# Fazendo download dos dados do mapa do Distrito Federal do site oficial do IBGE.

!wget -q "https://geoftp.ibge.gov.br/cartas_e_mapas/bases_cartograficas_continuas/bc100/go_df/versao2016/shapefile/bc100_go_df_shp.zip" -O distrito-federal.zip
!unzip -q distrito-federal.zip -d ./maps
!cp ./maps/LIM_Unidade_Federacao_A.shp ./distrito-federal.shp
!cp ./maps/LIM_Unidade_Federacao_A.shx ./distrito-federal.shx

mapa = geopandas.read_file("distrito-federal.shp")
mapa = mapa.loc[[0]]
mapa.head()

# Criando novo dataframe(geo_hub_df) a partir do deliveries_df
hub_df = deliveries_df[["region", "hub_lng", "hub_lat"]].drop_duplicates().reset_index(drop=True)
geo_hub_df = geopandas.GeoDataFrame(hub_df, geometry=geopandas.points_from_xy(hub_df["hub_lng"], hub_df["hub_lat"]))
geo_hub_df.head()

# Inserindo nova coluna 'geometry' na nova tabela
geo_deliveries_df = geopandas.GeoDataFrame(deliveries_df, geometry=geopandas.points_from_xy(deliveries_df["delivery_lng"], deliveries_df["delivery_lat"]))
geo_deliveries_df.head()

# Visualizar o gráfico com a biblioteca matplotlib


# cria o plot vazio
fig, ax = plt.subplots(figsize = (50/2.54, 50/2.54))

# plot mapa do distrito federal
mapa.plot(ax=ax, alpha=0.4, color="lightgrey")

# plot das entregas
geo_deliveries_df.query("region == 'df-0'").plot(ax=ax, markersize=1, color="red", label="df-0")
geo_deliveries_df.query("region == 'df-1'").plot(ax=ax, markersize=1, color="blue", label="df-1")
geo_deliveries_df.query("region == 'df-2'").plot(ax=ax, markersize=1, color="seagreen", label="df-2")

# plot dos hubs
geo_hub_df.plot(ax=ax, markersize=30, marker="x", color="black", label="hub")

# plot da legenda
plt.title("Entregas no Distrito Federal por Região", fontdict={"fontsize": 16})
lgnd = plt.legend(prop={"size": 15})
for handle in lgnd.legendHandles:
    handle.set_sizes([50])
	
plt.savefig(mapa-regiao.png)

plt.close(fig)

# Gráfico de entregas por região

# pegando colunas de interesse para o gráfico
data = pd.DataFrame(deliveries_df[['region', 'vehicle_capacity']].value_counts(normalize=True)).reset_index()
data.rename(columns={0: "region_percent"}, inplace=True)
data.head()

# visualizando o gráfico

import seaborn as sns

with sns.axes_style('whitegrid'):
  entregas-regiao = sns.barplot(data=data, x="region", y="region_percent", ci=None, palette="pastel")
  entregas-regiao.set(title='Proporção de entregas por região', xlabel='Região', ylabel='Proporção');
  
fig.savefig(entregas-regiao.png)

plt.close(fig)