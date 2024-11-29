"""
copyright: paul@mikadosoftware.com

so the adhoc row calc stuff is getting awkward.
I will extract every row, and see if I can find enought signal - I think : will
be useful

I haver broken this into two stages - first get a reasinable text extractin and
then convert that text to valid dataframe

the first part give us

['27', 'May,', '24', '16:01', '127', '83', '65', '1 June,', '24', '09:43', '145', '97', '72', '']
['1', 'June,', '24', '00:19', '133', '85', '73', '1 June,', '24', '09:51', '131', '83', '62', '']
['1', 'June,', '24', '00:36', '151', '98', '72', '1 June,', '24', '09:59', '135', '86', '60', '']
['1', 'June,', '24', '00:45', '137', '87', '76', '1 June,', '24', '13:19', '136', '85', '77', '']
['1', 'June,', '24', '00:54', '132', '84', '63', '1 June,', '24', '14:02', '138', '86', '76', '']
['1', 'June,', '24', '01:34', '122', '77', '61', '1 June,', '24', '14:10', '137', '86', '74', '']
['1', 'June,', '24', '02:54', '128', '81', '58', '1 June,', '24', '14:54', '132', '82', '65', '']
['1', 'June,', '24', '03:34', '138', '86', '74', '1 June,', '24', '15:03', '138', '86', '71', '']
['1', 'June,', '24', '04:14', '131', '83', '55', '1 June,', '24', '15:16', '136', '87', '64', '']
['1', 'June,', '24', '04:54', '121', '76', '53', '1 June,', '24', '15:30', '140', '88', '65', '']

there is some variablility but for the most part I think we can work with -
dates up to :, then three readings, 


[ ] for each day grab max and min and plot them
[ ] surely better ways with jupyter etc
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
import datetime

def test_process_rows():
    rows = [
['27', 'May,', '24', '16:01', '127', '83', '65', '1 June,', '24', '09:43', '145', '97', '72', ''],
['1', 'June,', '24', '00:19', '133', '85', '73', '1 June,', '24', '09:51', '131 83', '62', '', ''],
['1', '1', 'June,', '24', '00:36', '151', '98', '72', '1 June,', '24', '09:59','135', '86', '60'],
['1', '1', 'June,', '24', '00:36', '151', '98', '72']
]
    for row in rows:
        process_text_row(row)

def convertdates(timestring):
    """
    >>> convertdates("1June2400:19")
    2024-06-01 00:19:00
    """
    fmt = "%d%B%y%H:%M"
    return datetime.datetime.strptime(timestring, fmt)

def process_text_row(row):

    try:
        row = eval(row) #not great!
    except:
        return (None, None, None, None), (None, None, None, None)
    row_as_string = ' '.join(row)
    row_as_string = row_as_string.replace(',','')
    def extract_timeandreadings(row_as_string):

        #remove double spaces, clean up characters
        while '  ' in row_as_string:
            row_as_string = row_as_string.replace('  ',' ')

        #split up first set
        # we want to find the time, which works backawars to everything rles 
        # 27 May 24 16:01 127 83 65 1 June 24 09:43 145 97 72
        
        # find lh timestamp, then minutes, plus a space 16:01 ]
        idx = row_as_string.find(":") + 3
        lh_datetime = row_as_string[:idx].replace(" ", "")
        # we now should have the datetime, now grab the next three space
        # deliimited items
        remains = row_as_string[idx:]
        lh_bp = remains.strip().split(" ")[:3]
        delete_bp = ' '.join(lh_bp)
        remains = remains.replace(delete_bp, '').strip()
        return lh_datetime, lh_bp, remains
    lhtimestring, lh_readings, remains = extract_timeandreadings(row_as_string)
    lh_datetime = convertdates(lhtimestring)
    lh_sbp, lh_dbp, lh_hr = lh_readings

    if bool(remains):
        rhtimestring, rh_readings, remains1 = extract_timeandreadings(remains)   
        rh_datetime = convertdates(rhtimestring)
        rh_sbp, rh_dbp, rh_hr = rh_readings
    else:
        rh_datetime = None
        rh_sbp, rh_dbp, rh_hr = 0,0,0
    
    return (lh_datetime, lh_sbp, lh_dbp, lh_hr), (rh_datetime, rh_sbp, rh_dbp, rh_hr)


def grab_row(row, rawtgtpath):
    with open(rawtgtpath, 'a') as fo:
        fo.write(repr(row) + "\n")

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
    

def table_to_df_captureonly(tbl_extract, rawtgtpath):

    for row in find_bp_readings(tbl_extract):
        grab_row(row, rawtgtpath)
    df = pd.DataFrame()
    return df


def extract_pdf(filepath):
    """open `filepath` (assuming it is a formatted aktiia pdf report) and walk
    each page finding tables and extracting bp readings. """
    # decide where to store the raw readings
    basename = os.path.basename(filepath).replace(".pdf", ".raw")
    rawpath = os.path.join(READINGS, basename)
    
    doc = pymupdf.open(filepath) # open a document
    bigtable = pd.DataFrame()
    for c, page in enumerate(doc):
        foundtables = page.find_tables(strategy='text')
        for tbl in foundtables.tables:
            extract = tbl.extract()
            df = table_to_df_captureonly(extract, rawpath)              
                
            print(f'page: {c} {page.number}')
    return rawpath

def parse_intermediate_row_data(rawpath):
    ''' '''

    bodyrows = []
    with open(rawpath) as fo:
        txt = fo.read()
    for row in txt.split("\n"):
        lh, rh = process_text_row(row)
        if lh[0]:
            bodyrows.append(lh)
        if rh[0]:
            bodyrows.append(rh)
    df = pd.DataFrame(bodyrows, columns=['datetime', 'sbp', 'dbp','hr'])
    return df

def run(f):
    # walk through the pdf, extracting what we can into a intermedizte "raw"
    # format.
    basename = os.path.basename(f)
    rawpath = extract_pdf(f)
    # now from the raw (intermediate) figures we have, parse into df
    dframe = parse_intermediate_row_data(rawpath) 

    newloc = os.path.join(READINGS, basename.replace(".pdf", ".parq"))
    dframe.to_parquet(path=newloc)
    print(dframe)

def run_all_pdfs_on_disk():
    files = [f for f in os.listdir(FOLDER) if f.startswith('Aktiia')]
    for f in files:
        fpath = os.path.join(FOLDER, f)
        print(fpath)
        run(fpath)
        break

def plotit(dframe):
    import matplotlib.pyplot as plt
    import numpy as np

    # Data for plotting
    days = dframe['datetime'].to_list()
    x = []
    miny = []
    maxy = []
    for day in days:
        #take date, then  between 00 and 1159, then get those points and do min max
        st = datetime.datetime.combine(day, datetime.time.min)
        ed = datetime.datetime.combine(day, datetime.time.max)
     
        dframe1 = dframe[dframe['datetime'].between(st, ed)]
        sbpy = [int(i) for i in dframe1['sbp'].to_list()]
        miny.append(min(sbpy))
        maxy.append(max(sbpy))
        x.append(day)
        

    print(miny[:20], maxy[:20])
    fig, ax = plt.subplots()
    ax.plot(x, miny, 'bo')
    ax.plot(x, maxy, 'ro')

    ax.set(xlabel='time (s)', ylabel='sbp',
           title='plot')
    ax.grid()

    fig.savefig("test.png")
    plt.show()

FOLDER = '/home/pbrian/Downloads/'
READINGS = '/home/pbrian/Desktop/readings' 
if __name__ == '__main__':

    #run_all_pdfs_on_disk()
    dframe = pd.read_parquet(os.path.join(READINGS,
        'AktiiaReport_pb_Jun2024.parq')) 
    plotit(dframe)
    
