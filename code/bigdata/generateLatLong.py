#!/usr/bin/python
 
import sqlite3
import csv
import math
from sqlite3 import Error
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

      # makeCpNotH <- function(x) mapply(cpNotH,cpH=x,pH=ethnicity$probSchool)
      # makeBF <- function(x) {x <- 1.0E-9 + x;log10(x/sum(x*ethnicity$probSchool,na.rm=TRUE))} # Approximate

database = "C:\\Users\\cheekit\\Desktop\\score\\database.sqlite"

# create a database connection
conn = create_connection(database)
with conn:
    print("1. Query task by priority:")
    # select_task_by_priority(conn,1)

    cur = conn.cursor()
    # UGDS_WHITENH,UGDS_BLACKNH,UGDS_API,UGDS_AIANOld,UGDS_HISPOld
    cur.execute("""Select UNITID,LATITUDE,LONGITUDE From Scorecard 
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

 
    w = csv.writer(open("test(latlong).csv", "wb"))
    w.writerow(["UNITID","LATITUDE","LONGITUDE"])
    
    for row in rows:
        w.writerow(row)
        # print(row)