## 2016.02.01
## This script removes all non-international grants from the grants.gov downloadable XML database,
## reformats due dates & currency for easier readability, and removes garbage opps., i.e., the "this is a test, do not apply" opps.

__author__ = 'J.Sanderson'
__copyright__='Copyright 2016, J.Sanderson - The IGrants Project'
__email__='j-sanderson@jimu.kumamoto-u.ac.jp'
__license__='GPL'

import datetime, re, xml.etree.cElementTree as cElmTree
tree = cElmTree.parse('Database/GrantsDBExtract.xml')
root = tree.getroot()

# Replace 'FundingOppModSynopis' with 'FundingOppSynopsis' because
# we don't care about the difference, & merging makes processing easier.
for element in root.findall('FundingOppModSynopsis'):
    element.tag = 'FundingOppSynopsis'
    
# Reverting back to only using category 99 (from version 4). Cat. 25 contains too many non-int'l grants.
for FundingOppSynopsis in root.findall('FundingOppSynopsis'):
    IDs = [int(category.text) for category in FundingOppSynopsis.findall('EligibilityCategory')]
    if 99 not in IDs:
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
        if re.match("This is a test", title.text): 
            root.remove(FundingOppSynopsis)

tree.write('Output/IGrants-DB.xml', xml_declaration=True, encoding='UTF-8', method='xml')

# Append required header text.
import fileinput
processing_lineOne = False

for line in fileinput.input('Output/IGrants-DB.xml', inplace=1):
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
print('--> All non-international funding opportunities.')
print('--> Funding opportunities that expired before today,', datetime.datetime.now().date())
print('--> Garbage opportunities with titles such as "This is a test...do not apply".')
print('This script also formated the date & award ceiling strings for readability.')
print('*****')
print('Please place the "IGrants-DB.xml" output file into the appropriate URA_Web folder.')
print('~' * 80)
