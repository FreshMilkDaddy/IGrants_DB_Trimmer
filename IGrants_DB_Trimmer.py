__author__ = 'JMS'

from datetime import date
currentYear = date.today().year
import xml.etree.cElementTree as cElmTree
tree = cElmTree.parse('Database/GrantsDBExtract.xml')  #ADJUST ME!
root = tree.getroot()

# remove all non international grants
for FundingOppSynopsis in root.findall('FundingOppSynopsis'):
    IDs = [int(category.text) for category in FundingOppSynopsis.findall('EligibilityCategory')]
    if 99 not in IDs:
        root.remove(FundingOppSynopsis)

for FundingOppModSynopsis in root.findall('FundingOppModSynopsis'):
    mIDs = [int(category.text) for category in FundingOppModSynopsis.findall('EligibilityCategory')]
    if 99 not in mIDs:
        root.remove(FundingOppModSynopsis)

# remove all out of date grants
# noDueDates = 0  #currently not counting
for FundingOppSynopsis in root.findall('FundingOppSynopsis'):
	dDate = [int(dD.text[-4:]) for dD in FundingOppSynopsis.findall('ApplicationsDueDate')]
	if dDate < [currentYear]:
		root.remove(FundingOppSynopsis)

for FundingOppModSynopsis in root.findall('FundingOppModSynopsis'):
	dDate = [int(dD.text[-4:]) for dD in FundingOppModSynopsis.findall('ApplicationsDueDate')]
	if dDate < [currentYear]:
		root.remove(FundingOppModSynopsis)

tree.write("Output/IGrants.xml", xml_declaration=True, encoding='UTF-8', method="xml")

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
print('--> All non-international funding opportunities.')
print('--> Funding opportunities that expired before the year', currentYear)
print('Please place the "IGrants.xml" output file into the appropriate URA_Web folder.')
# print(' -' * 10)
# print('The number of funding opps with "None" as the due date is:', noDueDates)
print('~' * 80)
