"""
copyright: paul@mikadosoftware.com

so the adhoc row calc stuff is getting awkward.
I will extract every row, and see if I can find enought signal - I think : will
be useful


"""

HELPSTRING="""
Usage:
    aktiia_utils <filepath>
    aktiia_utils (-h | --help | --version)
        
Options:
    -h, --help  Show this screen and exit.

"""

import pymupdf
from pprint import pprint as pp
import pandas as pd
import os

def grab_row(row):
    with open('/tmp/foo.txt', 'a') as fo:
        fo.write(repr(row) + "\n")


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
    """ Given a table from pdf, find the rows of BP readings if any"""
    headerflag = False
    headerrow = []
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
            yield row
    

def table_to_df_captureonly(tbl_extract):

    for row in find_bp_readings(tbl_extract):
        grab_row(row)
    df = pd.DataFrame()
    return df

def table_to_df(tbl_extract):

    for row in find_bp_readings(tbl_extract):
    
            grab_row(row)
            lh, rh = None, None
            #lh,rh = convert_dual_row(row)
            if lh:
                bodyrows.append(lh)
            if rh:
                bodyrows.append(rh)
    df = pd.DataFrame(bodyrows, columns=['datetime', 'sbp', 'dbp','hr'])
    return df

def extract_pdf(filepath):
    """open `filepath` (assuming it is a formatted aktiia pdf report) and walk
    each page finding tables and extracting bp readings. """
    
    doc = pymupdf.open(filepath) # open a document
    bigtable = pd.DataFrame()
    for c, page in enumerate(doc):
        foundtables = page.find_tables(strategy='text')
        for tbl in foundtables.tables:
            extract = tbl.extract()
            df = table_to_df_captureonly(extract)              
                
            print(f'page: {c} {page.number}')
            if bigtable.empty:
                bigtable = df
            else:
                bigtable = pd.concat([bigtable, df], axis=0)
    return bigtable

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
    # f :'/home/pbrian/Downloads/AktiiaReport_pb_Nov2024.pdf'
    basename = os.path.basename(f)
    dframe = extract_pdf(f)
    newloc = os.path.join('/home/pbrian/Desktop/readings',
                          basename.replace(".pdf", ".csv"))
    #dframe.to_parquet(path=newloc)
    dframe.to_csv(path_or_buf=newloc) #using csv because no network atm so cannot pip
    print(dframe)

def foo():
    folder = '/home/pbrian/Downloads/'
    files = [f for f in os.listdir(folder) if f.startswith('Aktiia')]
    for f in files:
        fpath = os.path.join(folder, f)
        print(fpath)
        run(fpath)


if __name__ == '__main__':
    foo()

    #from docopt import docopt
    #args = docopt(HELPSTRING)
    #filepath = args['<filepath>']
    #run(filepath)

