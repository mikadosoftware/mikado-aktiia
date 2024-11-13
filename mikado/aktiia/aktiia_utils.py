#pip install --upgrade pymupdf
import pymupdf
from pprint import pprint as pp
import pandas as pd

def convert_dual_row(row):
    lh_date, lh_year, lh_time, lh_sbp, lh_dbp, lh_hr, rh_date, rh_year, rh_time, rh_sbp, rh_dbp, rh_hr,_ = row
    lh = [lh_date + " " + lh_year + " " + lh_time, lh_sbp, lh_dbp, lh_hr]
    rh = [rh_date + " " + rh_year + " " + rh_time, rh_sbp, rh_dbp, rh_hr]
    return [lh, rh]

def find_bp_readings(tbl_as_extract):
    headerflag = False
    headerrow = []
    bodyrows = []
    for row in tbl_as_extract:
        if row[0] == 'DATE':
            headerrow = row
            print(headerrow)
            input('gg')
            headerflag = True
            continue
        if headerflag:
            if row[0] == '':
                continue
            if row[0] == 'Initialization cuff measur':
                continue
            if row[0] == 'inquiries regarding this repor':
                continue
            if row[0] == 'ort was offered to you by Akti':
                continue
            lh,rh = convert_dual_row(row)
            bodyrows.append(lh)
            bodyrows.append(rh)
    df = pd.DataFrame(bodyrows, columns=['datetime', 'sbp', 'dbp','hr'])
    print(df)

def run():
    file = '/home/pbrian/Downloads/AktiiaReport_pb_Nov2024.pdf'
    doc = pymupdf.open(file) # open a document
    tables = []
    for c, page in enumerate(doc):
        foundtables = page.find_tables(strategy='text')
        #print(c, len(tbl.tables))

        #import pdb;pdb.set_trace()
        for tbl in foundtables.tables:
            extract = tbl.extract()
            find_bp_readings(extract)
            input('?')   

if __name__ == '__main__':
    run()

