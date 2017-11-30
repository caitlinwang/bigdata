import csv
from operator import itemgetter

with open('Scorecard4.csv', 'r') as f:
    data = [line for line in csv.reader(f)]

#sort by UNITID
header=data.pop(0)
UNITID_COLUMNID=0
ADM_RATE_COLUMNID=0
SATVR25_COLUMNID=0
del header[len(header)-1]
for col in range(len(header)):
    if(header[col]=="UNITID"):
        UNITID_COLUMNID=col
    if(header[col]=="ADM_RATE"):
        ADM_RATE_COLUMNID=col
    if(header[col]=="SATVR25"):
        SATVR25_COLUMNID=col



data.sort(key=itemgetter(UNITID_COLUMNID))  # 1 being the column number

print(data[0])
newdata=[]
schoolID=[]
count=0

#Summarise all the latest information in 1 row per school 
for row in data:
    count+=1
    if(count%1000==0):
        print("Row ",count)
    del row[len(row)-1]         #delete year as it is not relevant
    if(row[1] not in schoolID): #if new school
        schoolID.append(row[1])
        newdata.append(row)
    else:                       #if school exists
        temprow=newdata[len(newdata)-1]
        for col in range(len(row)):
            if(row[col]!="" or row[col]!="PrivacySuppressed"):
                temprow[col]=row[col]   #replace if lastest information exists
        newdata[(len(newdata))-1]=temprow


filteredData=[]
#Drop data without adm_rate, sat_score
for row in newdata:
    if(row[ADM_RATE_COLUMNID]!="" and row[SATVR25_COLUMNID]!=""):
        filteredData.append(row)

filteredData.insert(0,header)
w = csv.writer(open("Scorecard4(new).csv", "wb"))
for row in filteredData:
    w.writerow(row)


# print(len(school),school[0],school[1],school[len(school)-1])
# with open('movie_vertice.csv', 'rt') as ifile:
#     reader = csv.reader(ifile)

#     rownum = 0
#     schoolName=[]
#     schoolFeatures=[]
#     for row in reader:
#         if(rownum==0): #remove header
#             rownum=rownum+1
#             continue
        
#         # print(row)
#         budget.append(row[0])
#         popularity.append(row[4])
#         revenue.append(row[5])
#         runtime.append(row[6])
#         voting=float(row[8])
#         movieId=row[2]
#         dirGender.append(dirIdGenderdict[movieIdDirIddict[movieId]])
#         if(voting>=7):
#             rating.append(str(0))
#         elif(voting>6):
#             rating.append(str(1))
#         elif(True):
#             rating.append(str(2))
#         if row[1] not in genresEnum:
#             genresEnum.append(row[1])
#         for i in range(len(genresEnum)):
#             if(row[1]==genresEnum[i]):
#                 genres.append(i)
#         rownum=rownum+1

# print(genresEnum)

# with open('traindata.csv', "w", newline='') as ofile:
#     ofile2=open('testdata.csv', "w", newline='')
#     writer2 = csv.writer(ofile2,delimiter=',')
#     writer = csv.writer(ofile, delimiter=',')
#     threshold=(rownum-1)*0.8
#     for row in range(rownum-1):
#         if(row>=threshold):
#             data=[budget[row],popularity[row],revenue[row],runtime[row],genres[row],dirGender[row]]
#             writer2.writerow(data)
#         else:
#             data=[budget[row],popularity[row],revenue[row],runtime[row],genres[row],dirGender[row],rating[row]]
#             writer.writerow(data)
#         # writer.writerow(budget[row],popularity[row],revenue[row],runtime[row],genres[row])
#     ofile2.close()
#  