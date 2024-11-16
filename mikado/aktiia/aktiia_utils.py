import pymupdf
from pprint import pprint as pp
import pandas as pd
import os

def convert_dual_row(row):
    if len(row) == 13:
        lh_date, lh_year, lh_time, lh_sbp, lh_dbp, lh_hr, rh_date, rh_year, rh_time, rh_sbp, rh_dbp, rh_hr,_ = row
        lh = [lh_date + " " + lh_year + " " + lh_time, lh_sbp, lh_dbp, lh_hr]
        rh = [rh_date + " " + rh_year + " " + rh_time, rh_sbp, rh_dbp, rh_hr]
    elif len(row) == 14:
        #['8 November,', '24', '18:34', '135', '89', '65', '9', 'November,', '24', '05:03', '124', '77', '54', '']
        if len(row[0]) > 2: 
            lh_date, lh_year, lh_time, lh_sbp, lh_dbp, lh_hr, rh_day, rh_mth, rh_year, rh_time, rh_sbp, rh_dbp, rh_hr,_ = row
            rh_date = rh_day + " " + rh_mth 
        else:
        #['9', 'November,', '24', '19:27', '128', '82 57', '10', 'November,', '24', '21:37', '154', '96', '64', '']
            lh_day, lh_mth, lh_year, lh_time, lh_sbp, lh_dbp_hr,  rh_day, rh_mth, rh_year, rh_time, rh_sbp, rh_dbp, rh_hr,_ = row
            rh_date = rh_day + " " + rh_mth 
            lh_date = lh_day + " " + lh_mth
            lh_dbp, lh_hr = lh_dbp_hr.split(" ")

        lh = [lh_date + " " + lh_year + " " + lh_time, lh_sbp, lh_dbp, lh_hr]
        rh = [rh_date + " " + rh_year + " " + rh_time, rh_sbp, rh_dbp, rh_hr]

    elif len(row) == 7:
        #['1', '1 November,', '24', '15:37', '144', '90 82', '']
        lh_datetime = row[0]+row[1]+ " " + row[2] + " " + row[3]
        lh_sbp = row[4]
        try:
            lh_dbp, lh_hr = row[5].split(" ")
        except:
            import pdb;pdb.set_trace()
        lh = [lh_datetime, lh_sbp, lh_dbp, lh_hr]
        rh = None
    else:
        import pdb;pdb.set_trace()
    return [lh, rh]

def find_bp_readings(tbl_as_extract):
    headerflag = False
    headerrow = []
    bodyrows = []
    for row in tbl_as_extract:
        # bad table
        mightbetext = ''.join(row)
        if 'BP Readings' in mightbetext:
            input('readoing')
        if 'My Notes'.lower() in mightbetext.lower():
            return None
        if 'Summary Table'.lower() in mightbetext.lower():
            return None
        if 'DATE' in row:  #coul dbe in first or second position 
            headerrow = row
            headerflag = True
            continue
        
        if headerflag:
            outflag = False
            if row[0] == '':
                continue
            #mightbetext = ''.join(row)
            badtext = ('inquiries', 'quiries', 'ort', 'offered', 'cuff')
            for txt in badtext:
                if txt.lower() in mightbetext.lower():
                    outflag = True
            if outflag:
                continue
            # do we have two rows across page?
            lh,rh = convert_dual_row(row)
            if lh:
                bodyrows.append(lh)
            if rh:
                bodyrows.append(rh)
    df = pd.DataFrame(bodyrows, columns=['datetime', 'sbp', 'dbp','hr'])
    return df

def extract_pdf(filepath):

    
    doc = pymupdf.open(filepath) # open a document
    tables = pd.DataFrame()
    for c, page in enumerate(doc):
        foundtables = page.find_tables(strategy='text')
        for tbl in foundtables.tables:
            extract = tbl.extract()
            df = find_bp_readings(extract)
            print(f'page: {c} {page.number}')
            #print(df)
            if tables.empty:
                tables = df
            else:
                tables = pd.concat([tables, df], axis=0)
    print(tables)

def run2():

    file = '/home/pbrian/Downloads/AktiiaReport_pb_Nov2024.pdf'
    doc = pymupdf.open(file) # open a document
    tables = []

    page = doc[9]
    foundtables = page.find_tables(strategy='text')

    extract = foundtables.tables[0].extract()
    import pdb;pdb.set_trace()
    df = find_bp_readings(extract)
    print(df)

def run(f):
    f = f if f else '/home/pbrian/Downloads/AktiiaReport_pb_Nov2024.pdf'
    basename = os.path.basename(f)
    dframe = extract_pdf(f)
    newloc = os.path.join('/home/pbrian/Desktop/readings',
                          basename.replace(".pdf", ".parquet"))
    dframe.to_parquet(path=newloc)
    print(dframe)

if __name__ == '__main__':
    f = None
    run(f)

