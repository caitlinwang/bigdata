import sqlite3
import csv
from sqlite3 import Error
import sys
import sys

reload(sys)
sys.setdefaultencoding('utf8')

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return None

def select_task_by_priority(conn, priority):
    """
    Query tasks by priority
    :param conn: the Connection object
    :param priority:
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM Scorecard WHERE Id=?", (priority,))
 
    rows = cur.fetchall()
 
    for row in rows:
        print(row)
        
def cpNotH(cpH,pH):
    pEH=cpH*pH
    pE=sum(pEH)
    return ((pE-pEH)/(1-pH))

def BFactor(cpH,cpNotH):
    x=cpH/cpNotH
    return log10(x)

database = "/Users/hanbing/Desktop/BigDataAnalytics/FinalProject/database.sqlite"

# create a database connection
conn = create_connection(database)
with conn:
    print("1. Query task by priority:")
    # select_task_by_priority(conn,1)

    cur = conn.cursor()
    # UGDS_WHITENH,UGDS_BLACKNH,UGDS_API,UGDS_AIANOld,UGDS_HISPOld
    cur.execute("""Select UNITID,INSTNM,UGDS,CDR3,RPY_3YR_RT,RPY_5YR_RT,RPY_7YR_RT From Scorecard 
        WHERE Year=2013
        """)
    rows = cur.fetchall()
    rows1=list(rows)
    #rows1=[list(row) for row in rows]
    
    w = csv.writer(open("Scorecard(earnings)1.csv", "wb"))
    w.writerow(["UNITID","INSTNM","UGDS","CDR3","RPY_3YR_RT","RPY_5YR_RT","RPY_7YR_RT"])
    for row in rows:
        # row[0]=row[0].encode('utf-8')
        w.writerow(row)
        # print(row)
# create a database connection
conn = create_connection(database)
with conn:
    print("1. Query task by priority:")
    # select_task_by_priority(conn,1)

    cur = conn.cursor()
    # UGDS_WHITENH,UGDS_BLACKNH,UGDS_API,UGDS_AIANOld,UGDS_HISPOld
    cur.execute("""Select UNITID,INSTNM,UGDS,mn_earn_wne_p6,md_earn_wne_p6,pct10_earn_wne_p6,pct25_earn_wne_p6,pct75_earn_wne_p6,pct90_earn_wne_p6,sd_earn_wne_p6 From Scorecard 
        WHERE Year=2005
        """)
    rows = cur.fetchall()
    rows2=list(rows)
    #rows2=[list(row) for row in rows]
    w = csv.writer(open("Scorecard(earnings)2.csv", "wb"))
    w.writerow(["UNITID","INSTNM","UGDS","mn_earn_wne_p6","md_earn_wne_p6","pct10_earn_wne_p6","pct25_earn_wne_p6","pct75_earn_wne_p6","pct90_earn_wne_p6","sd_earn_wne_p6"])
    for row in rows:
        # row[0]=row[0].encode('utf-8')
        w.writerow(row)
        # print(row)
    colnames = cur.description

rows=rows1+rows2
rows[1]
colnames

import pandas as pd
import numpy as np
df1 = pd.read_csv('/Users/hanbing/Desktop/BigDataAnalytics/FinalProject/Scorecard(earnings)1.csv')
df2 = pd.read_csv('/Users/hanbing/Desktop/BigDataAnalytics/FinalProject/Scorecard(earnings)2.csv')

df = pd.merge(df1, df2, on='UNITID', how='inner')
df = df[['UNITID','INSTNM_x','UGDS_x','CDR3','RPY_3YR_RT','RPY_5YR_RT','RPY_7YR_RT','mn_earn_wne_p6','md_earn_wne_p6','pct10_earn_wne_p6','pct25_earn_wne_p6','pct75_earn_wne_p6','pct90_earn_wne_p6','sd_earn_wne_p6']]
df.rename(columns={'INSTNM_x': 'INSTNM','UGDS_x': 'UGDS'}, inplace=True)

data_columns = ['CDR3','RPY_3YR_RT','RPY_5YR_RT','RPY_7YR_RT','mn_earn_wne_p6','md_earn_wne_p6','pct10_earn_wne_p6','pct25_earn_wne_p6','pct75_earn_wne_p6','pct90_earn_wne_p6','sd_earn_wne_p6']
num_df = (df.drop(data_columns, axis=1).join(df[data_columns].apply(pd.to_numeric, errors='coerce')))
df = num_df[num_df[data_columns].notnull().all(axis=1)]

df['probSchool'] = df['UGDS']/(df['UGDS'].sum())
df['CDR3est'] = (df['CDR3']*df['UGDS'] + 10.0)/(df['UGDS'] + 10.0 + 140.0)
df['sdlog'] = np.sqrt(np.log((df['sd_earn_wne_p6']/df['mn_earn_wne_p6'])**2.0+1.0))
df['meanlog'] = np.log(df['mn_earn_wne_p6']**2/np.sqrt(df['mn_earn_wne_p6']**2+df['sd_earn_wne_p6']**2))

from scipy import stats
p_le30K = []
p_gt30Kle48K = []
p_gt48Kle75K = []
p_gt75Kle110K = []
p_gt110K = []
totprob = []
for i in range(df.shape[0]):
    sd = df.iloc[i:i+1]['sdlog']
    mean = df.iloc[i:i+1]['meanlog']
    distribution=stats.norm(mean,sd)
    p_le30K.append(distribution.cdf(30.0))
    p_gt30Kle48K.append(distribution.cdf(48.0)-distribution.cdf(30.0))
    p_gt48Kle75K.append(distribution.cdf(75.0E3)-distribution.cdf(48.0E3))
    p_gt75Kle110K.append(distribution.cdf(110.0E3)-distribution.cdf(75.0E3))
    p_gt110K.append(1-distribution.cdf(110.0E3))

#totprob = p_le30K + p_gt30Kle48K + p_gt48Kle75K + p_gt75Kle110K + p_gt110K
p_le30K = pd.DataFrame(p_le30K)
p_gt30Kle48K = pd.DataFrame(p_gt30Kle48K)
p_gt48Kle75K = pd.DataFrame(p_gt48Kle75K)
p_gt75Kle110K = pd.DataFrame(p_gt75Kle110K)
p_gt110K = pd.DataFrame(p_gt110K)

df['p_le30K']=p_le30K
df['p_gt30Kle48K']=p_gt30Kle48K
df['p_gt48Kle75K']=p_gt48Kle75K
df['p_gt75Kle110K']=p_gt75Kle110K
df['p_gt110K']=p_gt110K

l= ["CDR3","CDR3est","RPY_3YR_RT","RPY_5YR_RT","RPY_7YR_RT","p_le30K","p_gt30Kle48K","p_gt48Kle75K","p_gt75Kle110K","p_gt110K"]
for col in l:
    
    s = 'BF_' + col
    df[col] = df[col] + (1e-9) 
    df[s] = np.log10(df[col] / (df[col] * df['probSchool']).sum())

df_final = df[["UNITID","INSTNM","BF_CDR3","BF_CDR3est","BF_RPY_3YR_RT","BF_RPY_5YR_RT","BF_RPY_7YR_RT","BF_p_le30K","BF_p_gt30Kle48K","BF_p_gt48Kle75K","BF_p_gt75Kle110K","BF_p_gt110K"]]

df_final.to_csv('/Users/hanbing/Desktop/BigDataAnalytics/FinalProject/BF_Earnings.csv',index=False)

all_data = pd.read_csv('/Users/hanbing/Desktop/BigDataAnalytics/FinalProject/all.csv')
df_haha = df[['UNITID','mn_earn_wne_p6']]
all_data.rename(columns={'unitID': 'UNITID'}, inplace=True)
all_data = pd.merge(all_data, df_haha, on='UNITID', how='inner')
all_data.dtypes

all_data[['Rural','Town Remote', 'Town Distant','Small Suburb','Large Suburb','Small City','Mid City','Large City','FarWest','GreatLakes','MidEast','NewEngland','Plains','RockyMountains','SouthEast','SouthWest']] = all_data[['Rural','Town Remote', 'Town Distant','Small Suburb','Large Suburb','Small City','Mid City','Large City','FarWest','GreatLakes','MidEast','NewEngland','Plains','RockyMountains','SouthEast','SouthWest']]*0.5
all_data[['Town Remote']]

all_data.to_csv('/Users/hanbing/Desktop/BigDataAnalytics/FinalProject/all_new.csv',index=False)