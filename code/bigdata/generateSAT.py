#!/usr/bin/python
 
import sqlite3
import csv
import math
from sqlite3 import Error
import sys
from scipy import stats

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

# database = "C:\\Users\\cktang\\Google Drive\\Columbia\\EECSE6893 TOPICS-INFORMATION PROCESSING\\college-scorecard\\database.sqlite"
database = "C:\\Users\\cheekit\\Desktop\\score\\database.sqlite"

# create a database connection
conn = create_connection(database)
with conn:
    print("1. Query task by priority:")
    # select_task_by_priority(conn,1)

    cur = conn.cursor()
    
    # UGDS_WHITENH,UGDS_BLACKNH,UGDS_API,UGDS_AIANOld,UGDS_HISPOld
            # PCIP01,PCIP03,PCIP04,PCIP05,PCIP09,PCIP10,PCIP11,PCIP12,PCIP13,PCIP14,PCIP15,PCIP16,PCIP19,
        # PCIP22,PCIP23,PCIP24,PCIP25,PCIP26,PCIP27,PCIP29,PCIP30,PCIP31,PCIP38,PCIP39,PCIP40,PCIP41,PCIP42,PCIP43,PCIP44,PCIP45,PCIP46,
        # PCIP47,PCIP48,PCIP49,PCIP50,PCIP51,PCIP52,PCIP54,
    cur.execute("""Select UNITID,INSTNM,UGDS,

        (SATVR75+SATMT75-(SATVR25+SATMT25)) as IQR,SATVRMID,SATMTMID,SATWRMID,SAT_AVG,SAT_AVG_ALL
        From Scorecard 
        WHERE Year=2013 AND UGDS_WHITE!='' AND 
        CONTROL != 'Private for-profit' AND 
               CURROPER      == 'Currently certified as operating' AND 
               DISTANCEONLY    == 'Not distance-education only' AND 
               PREDDEG      == "Predominantly bachelor's-degree granting" AND 
               region      != 'U.S. Service Schools' AND 
               CCBASIC !='' AND 
               UGDS!='' AND 
               IQR!=''
        """)
    rows = cur.fetchall()

    # for row in rows:
    #     row[0]=row[0].encode('utf-8')
    
    #convert tuple to list
    rows=list(rows)
    rows=[list(row) for row in rows]
 
    w = csv.writer(open("test(sat).csv", "wb"))
    #"PCIP01","PCIP03","PCIP04","PCIP05","PCIP09","PCIP10","PCIP11","PCIP12","PCIP13","PCIP14","PCIP15","PCIP16","PCIP19","PCIP22","PCIP23","PCIP24","PCIP25","PCIP26","PCIP27","PCIP29","PCIP30","PCIP31","PCIP38","PCIP39","PCIP40","PCIP41","PCIP42","PCIP43","PCIP44","PCIP45","PCIP46","PCIP47","PCIP48","PCIP49","PCIP50","PCIP51","PCIP52","PCIP54"
    w.writerow(["UNITID","INSTNM","UGDS","IQR","SATVRMID","SATMTMID","SATWRMID","SAT_AVG","SAT_AVG_ALL","BF_lwr800","BF_800to1k","BF_1kto1.2k","BF_1.2kto1.4k","BF_gtr1.4k"])
    numOfStudents=0

    colnames = cur.description

    SATVR25_COLUMNID=0
    SATMT25_COLUMNID=0
    SATVR75_COLUMNID=0
    SATMT75_COLUMNID=0
    SAT_AVG_COLUMNID=0
    IQR_COLUMNID=0

    count=0
    for row in colnames:
        count=count+1
        if(row[0]=="IQR"):
            IQR_COLUMNID=count
        if(row[0]=="SAT_AVG"):
            SAT_AVG_COLUMNID=count


    #find total number of students
    for row in rows:
        numOfStudents+=row[2]

    numOfStudents=float(numOfStudents)
    newTable=[]
    initialLength = len(rows[0])
    for row in rows:
        #standard deviation is estimated to be IQR/1.35
        # print(row[IQR_COLUMNID])
        # print(len(row))
        sd=(row[IQR_COLUMNID])/1.35
        mean=row[SAT_AVG_COLUMNID]
        distribution=stats.norm(mean,sd)
        part1=distribution.cdf(800)
        part2=distribution.cdf(1000)-distribution.cdf(800)
        part3=distribution.cdf(1200)-distribution.cdf(1000)
        part4=distribution.cdf(1400)-distribution.cdf(1200)
        part5=1-distribution.cdf(1400)
        row.append(part1)
        row.append(part2)
        row.append(part3)
        row.append(part4)
        row.append(part5)

        probSchool=row[2]/numOfStudents
        newRow=[]
        newRow.append(part1*probSchool)
        newRow.append(part2*probSchool)
        newRow.append(part3*probSchool)
        newRow.append(part4*probSchool)
        newRow.append(part5*probSchool)
        # print(len(row))
        newTable.append(newRow)

    sumNewTable=[]
    #calculate sum of probSchool* cell
    for column in range(len(newTable[0])):
        sumNewTable.append(sum(row[column] for row in newTable))
    
    print(sumNewTable)
    for row in rows:
        for colCount in range(len(row)):
            if(colCount<initialLength):
                continue
            else:
                row[colCount] = 0.000000001+row[colCount]
                row[colCount] = math.log10(row[colCount]/(sumNewTable[colCount-initialLength]))
        w.writerow(row)
        # print(row)