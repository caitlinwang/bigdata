#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  9 14:17:22 2017

@author: apple
"""

# concatenate table and modify the column
import pandas as pd
ethnic_gender = pd.read_csv('ethnicBF.csv')
income = pd.read_csv('incomeBF.csv')
income = income [['unitID','BF_DEP_INC_PCT_LOx',
       'BF_DEP_INC_PCT_HI2x', 'BF_DEP_INC_GTLO_LTH2x', 'BF_IND_INC_PCT_LOx',
       'BF_IND_INC_PCT_HI2x', 'BF_IND_INC_GTLO_LTH2x']]

sat = pd.read_csv('SAT_BF.csv')
sat = sat[['UNITID','BF_lwr800', 'BF_800to1k', 'BF_1kto1.2k',
       'BF_1.2kto1.4k', 'BF_gtr1.4k']]

latlong = pd.read_csv('latlongBF.csv')
latlong = latlong[['UNITID','LATITUDE', 'LONGITUDE']]
latlong.rename(columns={'UNITID': 'unitID'}, inplace=True)

setting = pd.read_csv('settingBF.csv')
setting = setting[['unitID','BF_localeAggRural', 'BF_localeAggTownRemote',
       'BF_localeAggTownDistant',
       'BF_localeAggSuburbSmall/Midsize & Town:Fringe',
       'BF_localeAggSuburbLarge', 'BF_localeAggCitySmall',
       'BF_localeAggCityMidsize', 'BF_localeAggCityLarge',
       'BF_FarWest(AK,CA,HI,NV,OR,WA)', 'BF_GreatLakes(IL,IN,MI,OH,WI)',
       'BF_MidEast(DE,DC,MD,NJ,NY,PA)', 'BF_NewEngland(CT,ME,MA,NH,RI,VT)',
       'BF_Plains(IA,KS,MN,MO,NE,ND,SD)', 'BF_RockyMountains(CO,ID,MT,UT,WY)',
       'BF_Southeast(AL,AR,FL,GA,KY,LA,MS,NC,SC,TN,VA,WV)',
       'BF_Southwest(AZ,NM,OK,TX)']]

df1 = pd.read_csv('Scorecard(earnings)1.csv')
df2 = pd.read_csv('Scorecard(earnings)2.csv')
df3 = pd.merge(df1, df2, on='UNITID', how='inner')
df = df3[['UNITID','mn_earn_wne_p6']]
df.rename(columns={'UNITID': 'unitID'}, inplace=True)

egi = pd.merge(ethnic_gender, income, left_on='unitID', right_on='unitID')
egis = pd.merge(egi, sat, left_on='unitID', right_on='UNITID')
egiss =pd.merge(egis, setting, left_on='unitID', right_on='unitID')
egisss =pd.merge(egiss, df, left_on='unitID', right_on='unitID')
egissss =pd.merge(egisss, latlong, left_on='unitID', right_on='unitID')
egissss = egissss.drop(['Unnamed: 0'],axis = 1)
egissss = egissss.drop(['UNITID'],axis = 1)
egissss.columns = ['unitID','College','White','Black','Hispanic','Asian','AmericanIndianOrAlaskaNative',' NativeHawaiianOrPacificIslander',
                 'TwoOrMoreRaces','NonResidentAliens','RaceUnknown','Female','Dependent_30k','Dependent_30_110K','Dependent_110k',
                 'Independent_30k','Independent_30_110k','Independent_110k','lwr800','btwn800_1000','btwn1000_1200','btwn1200_1400','gtr1400','Rural','TownRemote',
                 'TownDistant','SmallSuburb','LargeSuburb','SmallCity','MidCity','LargeCity','FarWest','GreatLakes','MidEast','NewEngland','Plains','RockyMountains','SouthEast','SouthWest','mn_earn_wne_p6','Latitude','Longitude']
egissss[['Rural','TownRemote', 'TownDistant','SmallSuburb','LargeSuburb','SmallCity','MidCity','LargeCity','FarWest','GreatLakes','MidEast','NewEngland','Plains','RockyMountains','SouthEast','SouthWest']] *=0.5
egissss.to_csv('all.csv')
