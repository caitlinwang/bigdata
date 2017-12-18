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
    cur.execute("""Select UNITID,INSTNM,UGDS,UGDS_WHITE,UGDS_BLACK,UGDS_HISP,UGDS_ASIAN,UGDS_AIAN,UGDS_NHPI,UGDS_2MOR,UGDS_NRA,UGDS_UNKN From Scorecard 
        WHERE Year=2013 AND UGDS_WHITE!='' AND 
        CONTROL != 'Private for-profit' AND 
               CURROPER      == 'Currently certified as operating' AND 
               DISTANCEONLY    == 'Not distance-education only' AND 
               PREDDEG      == "Predominantly bachelor's-degree granting" AND 
               region      != 'U.S. Service Schools' AND 
               CCBASIC !='' AND 
               UGDS!=''
        """)
    rows = cur.fetchall()
 
    w = csv.writer(open("Scorecard(ethnic).csv", "wb"))
    w.writerow(["UNITID","INSTNM","UGDS","UGDS_WHITE","UGDS_BLACK","UGDS_HISP","UGDS_ASIAN","UGDS_AIAN","UGDS_NHPI","UGDS_2MOR","UGDS_NRA","UGDS_UNKN"])
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
    cur.execute("""Select UNITID,INSTNM,UGDS,pell_ever,fsend_1,fsend_2,fsend_3,fsend_4,fsend_5 From Scorecard 
        WHERE Year=2005
        """)
    rows = cur.fetchall()
 
    w = csv.writer(open("Scorecard(aid).csv", "wb"))
    w.writerow(["UNITID","INSTNM","UGDS","pell_over","fsend_1","fsend_2","fsend_3","fsend_4","fsend_5"])
    for row in rows:
        # row[0]=row[0].encode('utf-8')
        w.writerow(row)
        # print(row)

import pandas as pd
import numpy as np
df = pd.read_csv('/Users/hanbing/Desktop/BigDataAnalytics/FinalProject/Scorecard(aid).csv')
df['probSchool'] = df['UGDS']/(df['UGDS'].sum())
df['totprob'] = df['fsend_1']+df['fsend_2']+df['fsend_3']+df['fsend_4']+df['fsend_5']

l= ["pell_over","fsend_1","fsend_2","fsend_3","fsend_4","fsend_5"]
for col in l:
    
    s = 'BF_' + col
    df[col] = df[col] + (1e-9) 
    df[s] = np.log10(df[col] / (df[col] * df['probSchool']).sum())

df_final = df[['UNITID','INSTNM','BF_pell_over','BF_fsend_1','BF_fsend_2','BF_fsend_3','BF_fsend_4','BF_fsend_5']]

df_final.to_csv('/Users/hanbing/Desktop/BigDataAnalytics/FinalProject/BF_StudentAid.csv',index=False)