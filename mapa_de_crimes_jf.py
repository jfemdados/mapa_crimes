# -*- coding: utf-8 -*-
"""
Created on Sat Apr  2 09:48:46 2022

@author: User
"""

import pandas as pd
import glob
import numpy as np
import matplotlib.pyplot as plt
import geobr
import warnings
warnings.filterwarnings("ignore") 

#Mapa de Juiz de Fora
#https://github.com/ipeaGIT/geobr

bairro = geobr.read_neighborhood(year=2010)
bairros_geobr = bairro.loc[bairro["code_muni"]==3136702]
bairros_geobr["name_neighborhood"] = bairros_geobr["name_neighborhood"].str.upper().str.strip()


#------------------------------------------------------------#

#De-para de bairros geobr e pm
#O detalhamento da base da PM é maior que o Geobr, portanto usamos o de-para da prefeitura de Juiz de Fora para alocar
#mais bairros do detalhamento dentro de regiões maiores.

#https://www.pjf.mg.gov.br/institucional/cidade/mapas/mapa_central.php

de_para_geobr_pm = pd.read_excel(r"D:\Usuarios\Dell\Documents\1. Faculdade\1. TCC\de_para_bairros.xlsx")
de_para_geobr_pm['bairro_geobr'] = de_para_geobr_pm['bairro_geobr'] .str.upper().str.strip()
de_para_geobr_pm['bairro_pm'] = de_para_geobr_pm['bairro_pm'] .str.upper().str.strip()

#------------------------------------------------------------#

#Tratando string
#Removendo acentuação
de_para_geobr_pm['bairro_pm'] = de_para_geobr_pm['bairro_pm'].str.replace('Á', 'A').str.replace('É', 'E').str.replace('Ã', 'A').str.replace('Â', 'A').str.replace('Ú', 'U').str.replace('Ô', 'O').str.replace('Ó', 'O').str.replace('Ê', 'E').str.replace('Í', 'I').str.replace('Ç', 'C').str.replace('Ñ', 'N')
de_para_geobr_pm['bairro_geobr'] = de_para_geobr_pm['bairro_geobr'].str.replace('Á', 'A').str.replace('É', 'E').str.replace('Ã', 'A').str.replace('Â', 'A').str.replace('Ú', 'U').str.replace('Ô', 'O').str.replace('Ó', 'O').str.replace('Ê', 'E').str.replace('Í', 'I').str.replace('Ç', 'C')

#------------------------------------------------------------#

#Padronizando bairros
#Padronizando bairros do de-para da prefeitura
de_para_geobr_pm['bairro_geobr'] = de_para_geobr_pm['bairro_geobr'].str.replace('VILA OZANAN', 'OZANAN').str.replace('SANTO ANTONIO', 'SANTO ANTONIO DO PARAIBUNA').str.replace('LOURDES', 'NOSSA SENHORA DE LOURDES').str.replace('JOQUEI CLUBE', 'JOCKEY CLUB')

#Tratando bairros do Geobr para bater com a base da PM
bairros_geobr["name_neighborhood"] = bairros_geobr["name_neighborhood"].str.replace('Á', 'A').str.replace('É', 'E').str.replace('Ã', 'A').str.replace('Â', 'A').str.replace('Ú', 'U').str.replace('Ô', 'O').str.replace('Ó', 'O').str.replace('Ê', 'E').str.replace('Í', 'I').str.replace('Ç', 'C').str.replace("GRAMBERY","GRANBERY").str.replace("JOCKEY CLUB","JOQUEI CLUB").str.replace("CRUZEIRO DE SANTO ANTONIO","CRUZEIRO SANTO ANTONIO DO PARAIBUNA").str.replace("SANTA RITA DE CASSIA","SANTA RITA").str.replace("GRANJAS BETHANIA","GRANJAS BETANIA").str.replace("JARDIM PAINEIRAS","PAINEIRAS").str.replace("JARDIM SANTA HELENA","SANTA HELENA").str.replace("VILA FURTADO DE MENEZES","FURTADO DE MENEZES")

#------------------------------------------------------------#

#Criando um só dataframe para os dados da PM

path = r"D:\Usuarios\Dell\Documents\1. Faculdade\1. TCC\LAI_pm"
all_files = glob.glob(path + "/*.csv")

li = []

for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=0,sep=';',encoding='latin-1')
    li.append(df)

boletins = pd.concat(li, axis=0, ignore_index=True)

#Mais tratamento de bairros na base da PM
boletins["Bairro"] = boletins["Bairro"].str.replace("VALE DO YUNG","YUNG").str.replace("SAO LUCAS 2","SAO LUCAS").str.replace("SAO DAMIAO II","SAO DAMIAO").str.replace('Ç', 'C').str.replace('RECANTO DA MATA 2', 'RECANTO DA MATA').str.replace('OLAVO COSTA', 'VILA OLAVO COSTA').str.replace('RESIDENCIAL PORTAL DA TORRE', 'PORTAL DA TORRE').str.replace("AMAZONAS","AMAZONIA").str.replace("ARCO IRIS","ARCO-IRIS").str.replace('JOQUEI CLUBE','JOQUEI CLUB').str.replace('JUSCELINO KUBITSCHEK','JUSCELINO KUBITSCHECK').str.replace('JARDIM BOM CLIMA','JARDIM BONCLIMA').str.replace('NOSSA SENHORA DE LOURDES','LOURDES').str.replace('JARDIM ABC','PARQUE ABC')

#Merge da base da PM com o de-para da prefeitura para agrupar os bairros detalhados da PM em regiões maiores do geobr
boletins = boletins.merge(de_para_geobr_pm, left_on="Bairro", right_on='bairro_pm',how='left')
boletins['bairro_geobr'] = boletins['bairro_geobr'].fillna(boletins["Bairro"])


#------------------------------------------------------------#

#Criando a tabela dinâmica com o total de ocorrências por bairro
tot_crimes_bairro = pd.pivot_table(boletins, values= ['Qtde Ocorrências'],index=['bairro_geobr'],aggfunc=np.sum,fill_value=0)


# #Mapa de Ocorrencias

crimes_geolocalizados = bairros_geobr.merge(tot_crimes_bairro, left_on ="name_neighborhood",right_on = 'bairro_geobr', how="left")

#Colocando as ocorrências em escala logarítmica
crimes_geolocalizados['Qtde Ocorrências'] = crimes_geolocalizados['Qtde Ocorrências'].fillna(10)
crimes_geolocalizados['Qtde Ocorrências'] = np.log10(crimes_geolocalizados['Qtde Ocorrências'])

#Plotagem do mapa
plt.rcParams.update({"font.size": 5})

fig, ax = plt.subplots(figsize=(4, 4), dpi=2000)

crimes_geolocalizados.plot(
    column='Qtde Ocorrências',
    cmap='Reds',
    legend=True,
    edgecolor="#FEBF57",
    linewidth = 0.35,
    legend_kwds={
        "label": "$log_{10}$(Quantidade de Ocorrências)",
        "orientation": "vertical",
        "shrink": 0.6,
    },
    ax=ax,
)

ax.set_title("Boletins de Ocorrência - Juiz de Fora - 2016/2021")
ax.axis("off")


