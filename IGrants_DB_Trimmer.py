__author__ = 'J.Sanderson'
__copyright__='Copyright 2016, J.Sanderson - The IGrants Project'
__email__='j-sanderson@jimu.kumamoto-u.ac.jp'
__license__='GPL'
# finished adding the following on 2015.21.12:
# remove opps up to current date, not just year & sort by due dates
# reformat dates to and easier-to-read format (E.g., dd-mm-yyyy)
# format currency to easier-to-read format (E.g., ###,###,### - will note 'USD' in web table header)
# removed garbage opps, i.e., the "this is a test, do not apply" opps.

import datetime, re, xml.etree.cElementTree as cElmTree
# import locale ##not needed now
tree = cElmTree.parse('Database/GrantsDBExtract.xml')
root = tree.getroot()

# Replace 'FundingOppModSynopis' with 'FundingOppSynopsis' because
# we don't care about the difference, & merging makes processing easier.
for element in root.findall('FundingOppModSynopsis'):
    element.tag = 'FundingOppSynopsis'
	
# NEW: (28.11.2015): added category number 25 "other" to list --> only SOME are int'l
# ^is this a good idea?? --> how many 25s are international?? 
# (category 25s increase fund count by factor of 2-ish)
# OLD: remove all non international grants
for FundingOppSynopsis in root.findall('FundingOppSynopsis'):
    IDs = [int(category.text) for category in FundingOppSynopsis.findall('EligibilityCategory')]
    if 99 not in IDs and 25 not in IDs:      # if 99 not in IDs:  ##old
        root.remove(FundingOppSynopsis)

# remove all grants older than the day of full XML DB processing
for FundingOppSynopsis in root.findall('FundingOppSynopsis'):
    dDate = [datetime.datetime.strptime(dD.text, '%m%d%Y') for dD in FundingOppSynopsis.findall('ApplicationsDueDate')]
    if dDate < [datetime.datetime.now()]:
        root.remove(FundingOppSynopsis)

# reformat dates
for FundingOppSynopsis in root.findall('FundingOppSynopsis'):
    for dueDay in FundingOppSynopsis.findall('ApplicationsDueDate'):
        new_dD = datetime.datetime.strptime(dueDay.text, '%m%d%Y').date()
        dueDay.text = str(new_dD)

##sort by date
def getkey(elem):
    return elem.findtext("ApplicationsDueDate")

root[:] = sorted(root, key=getkey)

# integer check function
def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

## reformat currency (do this for EstimatedFunding & AwardFloor if needed)
for FundingOppSynopsis in root.findall('FundingOppSynopsis'):
    for awardCeiling in FundingOppSynopsis.findall('AwardCeiling'):
        if is_number(awardCeiling.text):
            awardCeiling.text = format(int(awardCeiling.text), ',d')

# remove the "test - don't apply" opps
for FundingOppSynopsis in root.findall('FundingOppSynopsis'):
    for title in FundingOppSynopsis.findall('FundingOppTitle'):
        if re.match("This is a test", title.text): #and re.match("do not submit", tstOpps):  #not needed??#
            root.remove(FundingOppSynopsis)

tree.write('Output/IGrants.xml', xml_declaration=True, encoding='UTF-8', method='xml')

# Append required header text.
import fileinput
processing_lineOne = False

for line in fileinput.input('Output/IGrants.xml', inplace=1):
    if line.startswith('<?xml version'):
        processing_lineOne = True
    else:
        if processing_lineOne:
            print('<?xml-stylesheet type="text/xsl" href="style.xsl"?>')
            print('<!DOCTYPE Grants SYSTEM "http://apply07.grants.gov/search/dtd/XMLExtract.dtd">')
        processing_lineOne = False
    print(line, end='')

print('~' * 80)
print('DONE! This script removed the following from the NIH grants database:')
print('--> MOST* non-international funding opportunities.')
print('--> Funding opportunities that expired before today,', datetime.datetime.now().date())
print('--> Garbage opportunities with titles such as "This is a test...do not apply".')
print('This script also formated the date & award ceiling strings for readability.')
print('*****')
print('--> *The Grants.Gov eligibility category of "Unrestricted" is international,')
print('-->  however, the "Other" category contains only some international opps.')
print('-->  Users or URAs should check the availablility of an opportunity of interest!')
print('Please place the "IGrants.xml" output file into the appropriate URA_Web folder.')
print('~' * 80)
