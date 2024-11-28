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

def test_process_rows():
    rows = [
['27', 'May,', '24', '16:01', '127', '83', '65', '1 June,', '24', '09:43', '145', '97', '72', ''],
['1', 'June,', '24', '00:19', '133', '85', '73', '1 June,', '24', '09:51', '131', '83', '62', ''],
['1', '1', 'June,', '24', '00:36', '151', '98', '72', '1 June,', '24', '09:59', '135', '86', '60']
]
    for row in rows:
        process_text_row(row)

def process_text_row(row):
    print(row)
    s = ' '.join(row)
    #remove double spaces, clean up characters
    while '  ' in s:
        s = s.replace('  ',' ')
    s = s.replace(',','')

    #split up first set
    # we want to find the time, which works backawars to everything rles 
    # 27 May 24 16:01 127 83 65 1 June 24 09:43 145 97 72
    
    # find lh timestamp, then minutes, plus a space 16:01 ]
    idx = s.find(":") + 3
    lh_datetime = s[:idx]
    # we now should have the datetime
    print(lh_datetime)
    remains = s[idx:]
    lh_bp = remains.strip().split(" ")[:3]
    print(lh_bp)

    x = ' '.join(lh_bp)
    idx2 = remains.find(x)+len(x)
    print(remains[idx2:])
    print(":" in remains)
    print('###############')


def grab_row(row):
    with open('/tmp/foo.txt', 'a') as fo:
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
    

def table_to_df_captureonly(tbl_extract):

    for row in find_bp_readings(tbl_extract):
        grab_row(row)
    df = pd.DataFrame()
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
    test_process_rows()
    #foo()

    #from docopt import docopt
    #args = docopt(HELPSTRING)
    #filepath = args['<filepath>']
    #run(filepath)

