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

    # for row in rows:
    #     row[0]=row[0].encode('utf-8')
    
    #convert tuple to list
    rows=list(rows)
    rows=[list(row) for row in rows]
 
    w = csv.writer(open("test(ethnic).csv", "wb"))
    w.writerow(["UNITID","INSTNM","UGDS","UGDS_WHITE","UGDS_BLACK","UGDS_HISP","UGDS_ASIAN","UGDS_AIAN","UGDS_NHPI","UGDS_2MOR","UGDS_NRA","UGDS_UNKN"])
    numOfStudents=0
    
    #find total number of students
    for row in rows:
        numOfStudents+=row[2]

    numOfStudents=float(numOfStudents)

    newTable=[]
    print("total students",numOfStudents)

    #create 1 more column of probSchool
    #and generate a new table of probSchool*ethnic cell
    for row in rows:
        colCount=0
        newRow=[]
        for col in row:
            colCount+=1
            if(colCount<4):
                continue
            else:
                newRow.append(row[2]/numOfStudents*col)
        row.append(row[2]/numOfStudents)
        newTable.append(newRow)
    sumNewTable=[]

    #calculate sum of probSchool*ethnic cell
    for column in range(len(newTable[0])):
        sumNewTable.append(sum(row[column] for row in newTable))
    
    for row in rows:
        for colCount in range(len(row)):
            if(colCount<3 or colCount==(len(row)-1)):
                continue
            else:
                row[colCount] = 0.000000001+row[colCount]
                row[colCount] = math.log10(row[colCount]/(sumNewTable[colCount-3]))
        
        w.writerow(row)
        # print(row)