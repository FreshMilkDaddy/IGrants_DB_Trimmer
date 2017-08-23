# Originally created: 2016.09.01
# This script removes MOST non-international grants from the grants.gov downloadable
#   XML database, reformats due dates & currency for easier readability, removes
#   garbage opps., i.e., the "this is a test, do not apply" opps, and adds hyperlinks
#   to the OppNums for use in the HTML table on the USA grants website.
# Updated for GdG v2.0 XML on 2017.01.02 (2017.08.23 - now on git)

import datetime
import fileinput
import re
import time

from lxml import etree

__author__ = 'J.M.Sanderson'
__copyright__ = 'Copyright 2016, J.M.Sanderson - The iGrants Project'
__email__ = 'j-sanderson@jimu.kumamoto-u.ac.jp'
__license__ = 'GPL'

# See how much time this shit takes to run. (End @ bottom) #
start = time.time()

parser = etree.XMLParser(ns_clean=True)
tree = etree.parse('Database/GrantsDBExtractv2.xml', parser)
root = tree.getroot()
ns = etree.QName(root, "html")  # namespace (use "ns.namespace")
# Use '{*}whateverthehell' for most namespace access##

# Replace 'forecast' with 'synopsis' for easier processing
for el in root.findall('{*}OpportunityForecastDetail_1_0'):
    el.tag = "{%s}OpportunitySynopsisDetail_1_0" % ns.namespace

# remove all grants older than the day of full XML DB processing
for el in root.findall('{*}OpportunitySynopsisDetail_1_0'):
    dDate = [datetime.datetime.strptime(dD.text, '%m%d%Y') for dD in el.findall('{*}CloseDate')]
    if dDate < [datetime.datetime.now()]:
        root.remove(el)

# NOTE: not all 25s are international
for el in root.findall('{*}OpportunitySynopsisDetail_1_0'):
    IDs = [int(category.text) for category in el.findall('{*}EligibleApplicants')]
    if 99 not in IDs and 25 not in IDs:
        root.remove(el)

# reformat dates
for dueDay in root.findall('.//{*}CloseDate'):
    new_dD = datetime.datetime.strptime(dueDay.text, '%m%d%Y').date()
    dueDay.text = str(new_dD)


# sort by date
def getkey(elem):
    return elem.findtext("{*}CloseDate")

root[:] = sorted(root, key=getkey)

# integer check function
def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

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
    if awardCeiling.text == "None" or awardCeiling.text == "0" or awardCeiling.text == None:
        awardCeiling.text = "NA"
    if is_number(awardCeiling.text):
        awardCeiling.text = format(int(awardCeiling.text), ',d')

# remove the "test - don't apply" opps  -- NOT NEEDED ANYMORE??
for oppSyn in root.findall('{*}OpportunitySynopsisDetail_1_0'):
    for title in oppSyn.findall('{*}OpportunityTitle'):
        if re.match("This is a test", title.text):
            root.remove(oppSyn)

# TRY:   elem.getparent().remove(elem)   with xpath

# print('Run time was about', round(end-start, 2), 'seconds.')

# There seems to be no standard way of declaring foreign eligibility.
# This won't catch all non-int'l-eligible grants but it cuts the grant list by ~1/3.
# Of particular problem are opps that don't use the word "foreign" at all.

# Remove all opps with certain wording about ineligibility in the
# "Additional Information on Eligibility" field, offices only serving the US, + other text
for oppSyn in root.findall('{*}OpportunitySynopsisDetail_1_0'):
    for otherCat in oppSyn.findall('{*}AdditionalInformationOnEligibility'):
        if re.search(
                r"^(?=.*foreign\b)(?=.*\borganizations\b|.*\binstitutions\b|.*\bentities\b)(?=.*\bnot eligible).*$",
                str(otherCat.text), flags=re.I):
            root.remove(oppSyn)

for oppSyn in root.findall('{*}OpportunitySynopsisDetail_1_0'):
    for otherCat in oppSyn.findall('{*}OpportunityCategoryExplanation'):
        if re.search(
                r"^(?=.*foreign\b)(?=.*\borganizations\b|.*\binstitutions\b|.*\bentities\b)(?=.*\bnot eligible).*$",
                str(otherCat.text), flags=re.I):
            root.remove(oppSyn)

for oppSyn in root.findall('{*}OpportunitySynopsisDetail_1_0'):
    for office in oppSyn.findall('{*}OpportunityTitle'):
        if re.search(r"^(?=.*Doctoral Dissertation).*$", str(office.text), flags=re.I):
            root.remove(oppSyn)

for oppSyn in root.findall('{*}OpportunitySynopsisDetail_1_0'):
    for office in oppSyn.findall('{*}AgencyCode'):
        if re.search(r"^(?=.*DOT).*$", str(office.text)) or re.search(r"^(?=.*USAID).*$", str(office.text)) or re.search(r"Bureau of Land Management", str(office.text)):
            root.remove(oppSyn)

for oppSyn in root.findall('{*}OpportunitySynopsisDetail_1_0'):
    for otherCat in oppSyn.findall('{*}AdditionalInformationOnEligibility'):
        if re.search(r"(?=.*\beligibility is limited to\b).*$", str(otherCat.text), flags=re.I):
            root.remove(oppSyn)

for oppSyn in root.findall('{*}OpportunitySynopsisDetail_1_0'):
    for otherCat in oppSyn.findall('{*}AdditionalInformationOnEligibility'):
        if re.search(r"(?=.*\beligible applicants are limited).*$", str(otherCat.text), flags=re.I):
            root.remove(oppSyn)

#Add HTML link to grants.gov oppIDs
oppIDs = [t.text for t in root.findall('.//{*}OpportunityID')]
oppNus = [t.text for t in root.findall('.//{*}OpportunityNumber')]

for idx, oppN in enumerate(root.findall('.//{*}OpportunityNumber')):
    oppN.text = '<a href="https://www.grants.gov/view-opportunity.html?oppId={0}" target="_blank">{1}</a>'.format(oppIDs[idx], oppNus[idx])

# For USA.htm database -> contains unrestricted (99s) and filtered other (25s)
tree.write('Output/IGrants-DB-v2.xml', xml_declaration=True, encoding='UTF-8', method='xml')

# Append required header text. #now to add the style sheet only.
processing_lineOne = False
for line in fileinput.input('Output/IGrants-DB-v2.xml', inplace=1):
    if line.startswith('<?xml version='):
        processing_lineOne = True
    else:
        if processing_lineOne:
            print('<?xml-stylesheet type="text/xsl" href="style v2.xsl"?>')
        # print('<!DOCTYPE Grants SYSTEM "http://apply07.grants.gov/search/dtd/XMLExtract.dtd">')
        processing_lineOne = False
    print(line, end='')


# For IGrants.htm calendar -> contains unrestricted (99s) ONLY
for el in root.findall('{*}OpportunitySynopsisDetail_1_0'):
    IDs = [int(category.text) for category in el.findall('{*}EligibleApplicants')]
    if 99 not in IDs:
        root.remove(el)

## Convert to .CSV (with proper headers) for upload to google calendars.

## Use .findall because xpath can't use namespaces
# titles = root.findall('.//{*}OpportunityTitle') #creates list of xml
# tits = []
# for t in titles:
#     tits.append(t.text)
## convert above to a list comprehension
# tits = [t.text for t in titles]

## list comprehention to pull text out of xml
## (basically a simplified version of the above)
##   5 lines reduced to 1
tits = [t.text for t in root.findall('.//{*}OpportunityTitle')]
ddat = [d.text for d in root.findall('.//{*}CloseDate')]
desc = [c.text for c in root.findall('.//{*}Description')]

hdr = ('Subject', 'Start Date', 'Start Time', 'End Date', 'End Time', 'All Day Event', 'Description', 'Location', 'Private')
mt = [""]*len(root)
tru = ["TRUE"]*len(root)
fal = ["FALSE"]*len(root)
rows = list(zip(tits, ddat, mt, ddat, mt, tru, desc, mt, fal)) #zip to change cols to rows

import csv

with open('Output/IGrants-Cal-v2.csv', 'w', newline='') as f:
    wtr = csv.writer(f, delimiter= ',', quoting=csv.QUOTE_ALL)
    wtr.writerow(hdr)
    wtr.writerows(rows)

# for speed testing #
end = time.time()

print('~' * 80)
print('DONE! Run time was approximately', round(end - start, 2), 'seconds.')
print('This script removed the following from the grants.gov database:')
print('--> All non-international funding opportunities for the iGrants Google calendar.')
print('--> Most non-international funding opportunities for the USA web page grants datatable.')
print('--> Funding opportunities that expired before today.')
print('--> Garbage opportunities with titles such as "This is a test...do not apply".')
print('This script also formated the date & award ceiling strings for readability.')
print('***     ***** TO USE *****     ***')
print('Place the "IGrants-DB-v2.xml" output file into the appropriate URA_Web folder.')
print('Upload the "IGrants-Cal-v2.csv" output file to the iGrants (USA) Google calendar.')
print("Don't forget to download the H2020 calendar (calls.ics) from the H2020 website,")
print('~' * 80)
