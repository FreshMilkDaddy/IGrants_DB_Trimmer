## 2016.02.01
## This script removes all non-international grants from the grants.gov downloadable XML database,
## reformats due dates & currency for easier readability, and removes garbage opps., i.e., the "this is a test, do not apply" opps.
##
## TESTING: Attempting to remove opps in cat. 25 that contain "not eligible to apply"-type text.
##   (see line 70~)

__author__ = 'J.Sanderson'
__copyright__='Copyright 2016, J.Sanderson - The IGrants Project'
__email__='j-sanderson@jimu.kumamoto-u.ac.jp'
__license__='GPL'

import datetime, re, xml.etree.cElementTree as cElmTree
# import locale ##not needed now
tree = cElmTree.parse('Database/GrantsDBExtract.xml')
root = tree.getroot()

# Replace 'FundingOppModSynopis' with 'FundingOppSynopsis' because
# we don't care about the difference, & merging makes processing easier.
for element in root.findall('FundingOppModSynopsis'):
    element.tag = 'FundingOppSynopsis'

# (category 25s increase fund count by factor of 2 to 4)
# NOTE: not all 25s are international
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

## reformat currency (also do this for EstimatedFunding & AwardFloor if needed)
for FundingOppSynopsis in root.findall('FundingOppSynopsis'):
    for awardCeiling in FundingOppSynopsis.findall('AwardCeiling'):
        if is_number(awardCeiling.text):
            awardCeiling.text = format(int(awardCeiling.text), ',d')
        if awardCeiling.text == "None" or awardCeiling.text == "0":
            awardCeiling.text = "NA"

# remove the "test - don't apply" opps
for FundingOppSynopsis in root.findall('FundingOppSynopsis'):
    for title in FundingOppSynopsis.findall('FundingOppTitle'):
        if re.match("This is a test", title.text): 
            root.remove(FundingOppSynopsis)

### TESTING ###  **Working well but needs further testing.**

## There seems to be no standard way of declaring foreign eligibility. 
## This won't catch all non-int'l-eligible grants but it cuts the list by ~1/3.
## Of particular problem are opps that don't use the word "foreign" at all...

# remove all opps with certain wording about ineligibility in the 
# "Additional Information on Eligibility" field, and other similar text
for FundingOppSynopsis in root.findall('FundingOppSynopsis'):
    for otherCat in FundingOppSynopsis.findall('AdditionalEligibilityInfo'):
        if re.search(r"^(?=.*foreign\b)(?=.*\borganizations\b|.*\binstitutions\b|.*\bentities\b)(?=.*\bnot eligible).*$", str(otherCat.text), flags=re.I):
            root.remove(FundingOppSynopsis)

for FundingOppSynopsis in root.findall('FundingOppSynopsis'):
    for otherCat in FundingOppSynopsis.findall('OtherCategoryExplanation'):
        if re.search(r"^(?=.*foreign\b)(?=.*\borganizations\b|.*\binstitutions\b|.*\bentities\b)(?=.*\bnot eligible).*$", str(otherCat.text), flags=re.I):
            root.remove(FundingOppSynopsis)

for FundingOppSynopsis in root.findall('FundingOppSynopsis'):
    for office in FundingOppSynopsis.findall('FundingOppTitle'):
        if re.search(r"^(?=.*Doctoral Dissertation).*$", str(office.text), flags=re.I):
            root.remove(FundingOppSynopsis)
           
for FundingOppSynopsis in root.findall('FundingOppSynopsis'):
    for office in FundingOppSynopsis.findall('Office'):
        if re.search(r"^(?=.*DOT).*$", str(office.text)) or re.search(r"^(?=.*USAID).*$", str(office.text)) or re.search(r"Bureau of Land Management", str(office.text)):
            root.remove(FundingOppSynopsis)

for FundingOppSynopsis in root.findall('FundingOppSynopsis'):
    for otherCat in FundingOppSynopsis.findall('AdditionalEligibilityInfo'):
        if re.search(r"(?=.*\beligibility is limited to\b).*$", str(otherCat.text), flags=re.I):
            root.remove(FundingOppSynopsis)

for FundingOppSynopsis in root.findall('FundingOppSynopsis'):
    for otherCat in FundingOppSynopsis.findall('AdditionalEligibilityInfo'):
        if re.search(r"(?=.*\beligible applicants are limited).*$", str(otherCat.text), flags=re.I):
            root.remove(FundingOppSynopsis)

### END TESTING ###


## For USA.htm database -> contains unrestricted (99s) and filtered other (25s)
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

## For IGrants.htm calendar -> contains unrestricted (99s) ONLY
##   For future: Convert to .CSV (with proper headers) for easy upload to google calendars. (Now using R.)
for FundingOppSynopsis in root.findall('FundingOppSynopsis'):
    IDs = [int(category.text) for category in FundingOppSynopsis.findall('EligibilityCategory')]
    if 99 not in IDs:
        root.remove(FundingOppSynopsis)

tree.write('Output/IGrants-Cal.xml', xml_declaration=True, encoding='UTF-8', method='xml')

# Append required header text.
import fileinput
processing_lineOne = False

for line in fileinput.input('Output/IGrants-Cal.xml', inplace=1):
    if line.startswith('<?xml version'):
        processing_lineOne = True
    else:
        if processing_lineOne:
            print('<?xml-stylesheet type="text/xsl" href="style.xsl"?>')
            print('<!DOCTYPE Grants SYSTEM "http://apply07.grants.gov/search/dtd/XMLExtract.dtd">')
        processing_lineOne = False
    print(line, end='')

print('~' * 80)
print('DONE! This script removed the following from the grants.gov database:')
print('--> All non-international funding opportunities for the iGrants Google calendar.')
print('--> Most non-international funding opportunities for the USA web page grants datatable.')
print('--> Funding opportunities that expired before today,', datetime.datetime.now().date())
print('--> Garbage opportunities with titles such as "This is a test...do not apply".')
print('This script also formated the date & award ceiling strings for readability.')
print('*****')
print('Please place the "IGrants-DB.xml" output file into the appropriate URA_Web folder.')
print('Please place the "IGrants-Cal.xml" output file into the Grants_dot_Gov R folder & process for use in the iGrants Google calendar.')
print("Don't forget to download the H2020 calendar (calls.ics) from the H2020 website.")
print('~' * 80)
