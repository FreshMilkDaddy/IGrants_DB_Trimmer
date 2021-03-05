#!/usr/bin/env python3
"""This script removes MOST non-international grants from the grants.gov downloadable XML database."""

import datetime
from dateutil.relativedelta import relativedelta
import fileinput
import re
import time  #for getting runtime
from lxml import etree

# Start timer (for testing)
start = time.time()

parser = etree.XMLParser(ns_clean=True)
tree = etree.parse('Data/GrantsDBExtractv2.xml', parser)
root = tree.getroot()
ns = etree.QName(root, "html")  # namespace (use "ns.namespace")
# Use '{*}whateverthehell' for most namespace access

# sort by date
def getkey(elem):
    return str(elem.findtext("{*}CloseDate"))

root[:] = sorted(root, key=getkey)

# integer check function
def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

# Replace 'forecast' with 'synopsis' for easier processing
for el in root.findall('{*}OpportunityForecastDetail_1_0'):
    el.tag = "{%s}OpportunitySynopsisDetail_1_0" % ns.namespace

# remove all grants older than 6 months after the day of XML DB processing (providing time to write grant application)
for el in root.findall('{*}OpportunitySynopsisDetail_1_0'):
    dDate = [datetime.datetime.strptime(dD.text, '%m%d%Y') for dD in el.findall('{*}CloseDate')]
    if dDate < [datetime.datetime.now() + relativedelta(months = +6)]:
        root.remove(el)

# keep only NIH data (since they are the best option for international cooperation)
for oppSyn in root.findall('{*}OpportunitySynopsisDetail_1_0'):
    for nih in oppSyn.findall('{*}AgencyName'):
        if nih.text != "National Institutes of Health":
            root.remove(oppSyn)

# reformat dates
for dueDay in root.findall('.//{*}CloseDate'):
    new_dD = datetime.datetime.strptime(dueDay.text, '%m%d%Y').date()
    dueDay.text = str(new_dD)

# add missing AwardCeiling elements as needed
cashMoney = root.findall('.//{*}AwardCeiling')
if len(cashMoney) < len(root):
    putitinthere = "{http://apply.grants.gov/system/OpportunityDetail-V1.0}AwardCeiling"
    for oppSyn in root.findall('{*}OpportunitySynopsisDetail_1_0'):
        node = oppSyn.find(putitinthere)
        if node is None:
            oppSyn.append(etree.Element("{%s}AwardCeiling" % ns.namespace))

# reformat currency
for awardCeiling in root.findall('.//{*}AwardCeiling'):
    if awardCeiling.text == "None" or awardCeiling.text == "0" or awardCeiling.text is None:
        awardCeiling.text = "NA"
    if is_number(awardCeiling.text):
        awardCeiling.text = format(int(awardCeiling.text), ',d') 

# remove opps with the text "(Foreign Institutions) are not eligible to apply" in AdditionalInformationOnEligibility 
for oppSyn in root.findall('{*}OpportunitySynopsisDetail_1_0'):
    for otherCat in oppSyn.findall('{*}AdditionalInformationOnEligibility'):
        if re.search(r"\(Foreign Institutions\) are not eligible to apply", str(otherCat.text), flags=re.I):
            root.remove(oppSyn)

# XML output
tree.write('Output/IGrants-DB-v2.xml', xml_declaration=True, encoding='UTF-8', method='xml')

# Append required header text. #now to add the style sheet only.
processing_lineOne = False
for line in fileinput.input('Output/IGrants-DB-v2.xml', inplace=1):
    if line.startswith('<?xml version='):
        processing_lineOne = True
    else:
        if processing_lineOne:
            print('<?xml-stylesheet type="text/xsl" href="style v2.xsl"?>')
        processing_lineOne = False
    print(line, end='')

## Convert to .CSV (with proper headers) for upload to google calendars.
tits = [t.text for t in root.findall('.//{*}OpportunityTitle')]
ddat = [d.text for d in root.findall('.//{*}CloseDate')]
desc = [c.text for c in root.findall('.//{*}Description')]

hdr = ('Subject', 'Start Date', 'Start Time', 'End Date', 'End Time', 'All Day Event', 'Description', 'Location', 'Private')
mt = [""]*len(root)
tru = ["TRUE"]*len(root)
fal = ["FALSE"]*len(root)
rows = list(zip(tits, ddat, mt, ddat, mt, tru, desc, mt, fal))  # "zip" changes cols to rows

import csv

with open('Output/IGrants-Cal-v2.csv', 'w', newline='') as f:
    wtr = csv.writer(f, delimiter= ',', quoting=csv.QUOTE_ALL)
    wtr.writerow(hdr)
    wtr.writerows(rows)

# for speed testing #
end = time.time()

print('~' * 80)
print('DONE! Run time was approximately', round(end - start, 2), 'seconds.')
print('This script performed the following actions on the grants.gov XML database:')
print('--> Extracted only NIH grants and removed expired grants.')
print('--> Attempted to remove grants not available to international applicants.')
print('--> Formated the date & award amount strings for readability.\n')
print('               ***     ***** TO USE *****     ***\n')
print('1) Place the "IGrants-DB-v2.xml" output file into the appropriate URA_Web folder.')
print('2) Upload "IGrants-Cal-v2.csv" output file to the iGrants (USA) Google calendar.')
print("~ Don't forget to process the HORIZON calendar for grants from the EU, ~")
print('~' * 80)