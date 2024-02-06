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
#

# faça o código de exploração de dados:
!wget -q "https://raw.githubusercontent.com/andre-marcos-perez/ebac-course-utils/main/dataset/deliveries.json" -O deliveries.json

# - coleta de dados;
with open('deliveries.json', mode='r', encoding='utf-8') as arquivo:
  data = json.load(arquivo)

# - wrangling da estrutura;
deliveries_df = pd.DataFrame(data)

# - exploração do schema;
deliveries_df.head()

# Quebrando coluna origin;
hub_origin_df = pd.json_normalize(deliveries_df["origin"])

# Concatenando as 2 tabelas;
deliveries_df = pd.merge(left=deliveries_df, right=hub_origin_df, how='inner', left_index=True, right_index=True)

# excluindo coluna origin;
deliveries_df = deliveries_df.drop("origin", axis=1)

# arrumando ordem da tabela;
deliveries_df = deliveries_df[["name", "region", "lng", "lat", "vehicle_capacity", "deliveries"]]
# renomeando colunas 'lng' e 'lat';
deliveries_df.rename(columns={"lng": "hub_lng", "lat": "hub_lat"}, inplace=True)

# Normalizando a coluna deliveries
deliveries_exploded_df = deliveries_df[["deliveries"]].explode("deliveries")

# Quebrando coluna deliveries;
deliveries_normalized_df = pd.concat([
  pd.DataFrame(deliveries_exploded_df["deliveries"].apply(lambda record: record["size"])).rename(columns={"deliveries": "delivery_size"}),
  pd.DataFrame(deliveries_exploded_df["deliveries"].apply(lambda record: record["point"]["lng"])).rename(columns={"deliveries": "delivery_lng"}),
  pd.DataFrame(deliveries_exploded_df["deliveries"].apply(lambda record: record["point"]["lat"])).rename(columns={"deliveries": "delivery_lat"}),
], axis= 1)

# Excluindo coluna deliveries;
deliveries_df = deliveries_df.drop("deliveries", axis=1)
# anexando as 2 tabelas;
deliveries_df = pd.merge(left=deliveries_df, right=deliveries_normalized_df, how='right', left_index=True, right_index=True)
deliveries_df.reset_index(inplace=True, drop=True)

# Verificando tipo de dados e valores faltantes
deliveries_df.info()

# Verificando atributos categóricos (não numéricos);
deliveries_df.select_dtypes("object").describe().transpose()

# Verificando dados faltantes;
deliveries_df.isna().any()

# Verificando quantidade de valores faltantes por coluna;
deliveries_df.isna().sum()

# Verificando valores faltantes nas colunas categóricas;
deliveries_df.select_dtypes(include=['object']).isna().sum()

# Verificando valores faltantes nas colunas do tipo int;
deliveries_df.select_dtypes(include=['int64']).isna().sum()

# Verificando valores faltantes nas colunas do tipo float;
deliveries_df.select_dtypes(include=['float64']).isna().sum()

# Visualizar tabela
deliveries_df.head()

# faça o código de manipulação de dados:

# - Geolocalização do hub;
hub_df = deliveries_df[["region", "hub_lng", "hub_lat"]]
hub_df = hub_df.drop_duplicates().sort_values(by="region").reset_index(drop=True)
hub_df.head()

# Utilizando biblioteca geopy;
geolocator = Nominatim(user_agent="ebac_geocoder")
location = geolocator.reverse("-15.657013854445248, -47.802664728268745")

print(json.dumps(location.raw, indent=2, ensure_ascii=False))

# Extraindo informações de cidades e bairros baseados nas coordenadas das três regiões;
from geopy.extra.rate_limiter import RateLimiter
geocoder = RateLimiter(geolocator.reverse, min_delay_seconds=1)

hub_df["coordinates"] = hub_df["hub_lat"].astype(str)  + ", " + hub_df["hub_lng"].astype(str)
hub_df["geodata"] = hub_df["coordinates"].apply(geocoder)
hub_df.head()

# Normalizando coluna geodata;
hub_geodata_df = pd.json_normalize(hub_df["geodata"].apply(lambda data: data.raw))
hub_geodata_df.head()

# Verificando colunas da tabela;
hub_geodata_df.columns

# Selecionando colunas "address.town", "address.suburb", "address.city";
hub_geodata_df = hub_geodata_df[["address.town", "address.suburb", "address.city"]]
# Renomeando colunas selecionadas;
hub_geodata_df.rename(columns={"address.town": "hub_town", "address.suburb": "hub_suburb", "address.city": "hub_city"}, inplace=True)
hub_geodata_df["hub_city"] = np.where(hub_geodata_df["hub_city"].notna(), hub_geodata_df["hub_city"], hub_geodata_df["hub_town"])
hub_geodata_df["hub_suburb"] = np.where(hub_geodata_df["hub_suburb"].notna(), hub_geodata_df["hub_suburb"], hub_geodata_df["hub_city"])
hub_geodata_df = hub_geodata_df.drop("hub_town", axis=1)
hub_geodata_df.head()

# Selecionando colunas de interesse;
hub_df = pd.merge(left=hub_df, right=hub_geodata_df, left_index=True, right_index=True)
hub_df = hub_df[["region", "hub_suburb", "hub_city"]]
hub_df.head()

# Anexando as colunas de interesse ao dataframe original;
deliveries_df = pd.merge(left=deliveries_df, right=hub_df, how="inner", on="region")
# Organizando colunas;
deliveries_df = deliveries_df[["name", "region", "hub_lng", "hub_lat", "hub_city", "hub_suburb", "vehicle_capacity", "delivery_size", "delivery_lng", "delivery_lat"]]
deliveries_df.head()

# Geocodificação reversa da entrega

!wget -q "https://raw.githubusercontent.com/andre-marcos-perez/ebac-course-utils/main/dataset/deliveries-geodata.csv" -O deliveries-geodata.csv

deliveries_geodata_df = pd.read_csv("deliveries-geodata.csv")
deliveries_geodata_df.head()

# Anexando as 2 tabelas;
deliveries_df = pd.merge(left=deliveries_df, right=deliveries_geodata_df[["delivery_city", "delivery_suburb"]], how="inner", left_index=True, right_index=True)
deliveries_df.head()

# Verificando valores faltantes
deliveries_df.info()

deliveries_df.isna().any()

# Salvar em arquivo CSV

deliveries_df.to_csv('tabela-deliveries.csv', sep=',', index=False)