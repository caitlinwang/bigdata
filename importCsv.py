import csv
import sqlite3

# Process data dictionary
sqlite_types = {
    "integer": "INTEGER",
    "string":  "TEXT",
    "float":   "REAL"
}
name_col=4
type_col=5
value_col=7
label_col=8
previous_col = None
columns = {}
for (i, row) in enumerate(csv.reader(open("C:/Users/cheekit/Desktop/score/CollegeScorecardDataDictionary-09-12-2015.csv"))):
    if i==0:
        assert row[name_col]=="VARIABLE NAME"
        assert row[type_col]=="API data type"
        assert row[value_col]=="VALUE"
        assert row[label_col]=="LABEL"
        continue
    if row[name_col].strip() != "":
        previous_col = row[name_col]
        if row[type_col]=="integer" and row[value_col].strip() != "":
            assert row[label_col].strip() != ""
            columns[row[name_col]] = {"type": sqlite_types["string"],
                                      "key": {row[value_col]: row[label_col]}}
        elif row[type_col] in sqlite_types:
            assert row[value_col].strip() == ""
            columns[row[name_col]] = {"type": sqlite_types[row[type_col]]}
        else:
            raise Exception("Unexpected type: %s" % row[type_col])
    else:
        assert row[value_col] != ""
        assert row[label_col] != ""
        columns[previous_col]["key"][row[value_col]] = row[label_col]
print(len(columns))
columns["Year"] = {"type": sqlite_types["integer"]}
columns["Id"]   = {"type": "INTEGER PRIMARY KEY"}

# Correcting errors in dictionary/data combination
for col in ["CIP01CERT1", "CIP01CERT2", "CIP01ASSOC"]:
    if "0" not in columns[col]["key"]:
        columns[col]["key"]["0"] = "Program not offered"
    if "1" not in columns[col]["key"]:
        columns[col]["key"]["1"] = "Program offered"
    if "2" not in columns[col]["key"]:
        columns[col]["key"]["2"] = "Program offered through an exclusively distance-education program"
if "68" not in columns["st_fips"]["key"]:
    columns["st_fips"]["key"]["68"] = "Unknown"
if "0" not in columns["CCUGPROF"]["key"]:
    columns["CCUGPROF"]["key"]["0"] = "Unknown"

# Process data files
years = range(1996, 2014)
filename_from_year = lambda year: "C:/Users/cheekit/Desktop/score/MERGED%d_PP.csv" % year

r = csv.reader(open(filename_from_year(years[0])))
rows = list(r)
header_raw = rows[0]
w = csv.writer(open("C:/Users/cheekit/Desktop/score/Scorecard4.csv", "wb"))

#filter
old_header_raw = header_raw
colList=[1,4,5,6,14,17]+list(range(37,62))+list(range(377,383))+[386,438,1639,1640]
# colList=list(range(1,9))+list(range(15,16))+list(range(17,21))+list(range(38,63))+list(range(292,293))+list(range(378,385))+list(range(1505,1507))+list(range(1640,1642))
print(colList)
newrow=[]
colnum=0
print(type(header_raw),len(header_raw),type(header_raw[0]),header_raw[0])
# splittedrow=header_raw.split(',')
for col in header_raw:
    colnum+=1
    if colnum not in colList:
        if(columns.get(col)!=None):
            del columns[col]
        continue
    else:
        newrow+=[col]
header_raw=newrow
print(len(columns))
print(type(header_raw),len(header_raw),type(header_raw[0]),header_raw[0])

print(type(columns),len(columns))


if header_raw[0]=="\xef\xbb\xbfUNITID":
    print("removing unicode from header")
    header = ["UNITID"] + header_raw[1:] + ["Year"]
else:
    header = header_raw + ["Year"]
header = ["Id"] + header
# print(header[0:10])
for missing in set(header).difference(set(columns.keys())):
    print("Adding column %s as string type" % missing)
    columns[missing] = {"type": sqlite_types["string"]}

in_dictionary_not_header = set(columns.keys()).difference(set(header))
if in_dictionary_not_header:
    raise Exception("Not handling case where items in dictionary aren't in header: %s" % in_dictionary_not_header)


w.writerow(header)

sqlite_schema = ["    %s %s," % (col, columns[col]["type"]) for col in header]
sqlite_schema[-1] = sqlite_schema[-1][:-1] + ");"
sqlite_schema = ["CREATE TABLE Scorecard ("] + sqlite_schema
sqlite_schema = "\n".join(sqlite_schema)
conn = sqlite3.connect("C:/Users/cheekit/Desktop/score/database4.sqlite")
conn.text_factory = lambda x: unicode(x, "utf-8", "ignore")
curs = conn.cursor()
curs.execute(sqlite_schema)

def transform(x, col_name, columns):
    if x=="NULL":
        return ""
    if "key" in columns[col_name]:
        try:
            return columns[col_name]["key"][x]
        except:
            print("Key %s not found in column %s" %(x, col_name))
    return x

row_id=0
     
for year in years:
    rows = list(csv.reader(open(filename_from_year(year))))
    if old_header_raw != rows[0]:
    # if header_raw != rows[0]:
        raise Exception("Different headers")
    for row in rows[1:]:
        colnum=0
        newrow=[]
        for col in row:
            colnum+=1
            if colnum not in colList:
                continue
            else:
                newrow+=[col]
        row=newrow
        if row_id % 1000 == 0:
            print("row: %d" % row_id)
        row_id += 1
        row = [row_id] + row + [str(year)]
        row = [transform(row[i], col, columns) for (i, col) in enumerate(header)]
        insert_statement = "INSERT INTO Scorecard (%s) VALUES (%s)" % (",".join([col for (i, col) in enumerate(header) if row[i]]), ",".join(["?" for el in row if el]))
        curs.execute(insert_statement, [el for el in row if el])
        # update_statement = "UPDATE Scorecard SET %s WHERE Id=%d" % (",".join([col+"=?" for (i, col) in enumerate(header[30:]) if row[i+30]]), row_id)
        # curs.execute(update_statement, [el for el in row[30:] if el])
        w.writerow(row)

conn.commit()

curs = conn.cursor()
curs.execute("CREATE INDEX scorecard_instnm_ix ON Scorecard (INSTNM);")
conn.commit()

curs = conn.cursor()
curs.execute("VACUUM;")
conn.commit()