#!/usr/bin/env python3
"""This script removes MOST non-international grants from the grants.gov downloadable XML database."""

import datetime
import fileinput
import re
import time
from lxml import etree

# Start timer (for testing)
# start = time.time()

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

# remove all grants older than the day of XML DB processing
for el in root.findall('{*}OpportunitySynopsisDetail_1_0'):
    dDate = [datetime.datetime.strptime(dD.text, '%m%d%Y') for dD in el.findall('{*}CloseDate')]
    if dDate < [datetime.datetime.now()]:
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

# There seems to be no standard way of declaring foreign eligibility.
# This won't catch all non-int'l-eligible grants but it cuts the grant list by ~1/3.
# Of particular problem are opps that don't use the word "foreign" at all.

for oppSyn in root.findall('{*}OpportunitySynopsisDetail_1_0'):
    for otherCat in oppSyn.findall('{*}AdditionalInformationOnEligibility'):
        if re.search(r"^(?=.*foreign\b)(?=.*\borganizations\b|.*\binstitutions\b|.*\bentities\b)(?=.*\bnot eligible)(?=.*\beligibility is limited to\b)(?=.*\beligible applicants are limited).*$", str(otherCat.text), flags=re.I):
            root.remove(oppSyn)


"""  function to remove elements by specific tag using regex
def Regex_to_Remove_XML_item(srchTag, srchStrng):
    for oppSyn in root.findall('{*}OpportunitySynopsisDetail_1_0'):
        for someTag in oppSyn.findall(srchTag):
            if re.search(srchStrng, str(someTag.text), flags=re.I):
                root.remove(oppSyn) 

# remove elements
Regex_to_Remove_XML_item('{*}AdditionalInformationOnEligibility', r"^(?=.*foreign\b)(?=.*\borganizations\b|.*\binstitutions\b|.*\bentities\b)(?=.*\bnot eligible).*$")
Regex_to_Remove_XML_item('{*}OpportunityCategoryExplanation', r"^(?=.*foreign\b)(?=.*\borganizations\b|.*\binstitutions\b|.*\bentities\b)(?=.*\bnot eligible).*$")
Regex_to_Remove_XML_item('{*}OpportunityTitle', r"^(?=.*Doctoral Dissertation).*$")
Regex_to_Remove_XML_item('{*}OpportunityTitle', r"^(?=.*test).*$")
Regex_to_Remove_XML_item('{*}AgencyCode', r"^(?=.*DOD).*$")
Regex_to_Remove_XML_item('{*}AgencyCode', r"^(?=.*DOI).*$")
Regex_to_Remove_XML_item('{*}AgencyCode', r"^(?=.*VA).*$")
Regex_to_Remove_XML_item('{*}AgencyCode', r"^(?=.*DOT).*$")
Regex_to_Remove_XML_item('{*}AgencyCode', r"^(?=.*DOS).*$")
Regex_to_Remove_XML_item('{*}AgencyCode', r"^(?=.*DOL).*$")
Regex_to_Remove_XML_item('{*}AgencyCode', r"^(?=.*USAID-).*$")
Regex_to_Remove_XML_item('{*}AgencyCode', r"^(?=.*CNCS).*$")
Regex_to_Remove_XML_item('{*}AgencyCode', r"^(?=.*USDA).*$")
Regex_to_Remove_XML_item('{*}AgencyCode', r"^(?=.*DOC).*$")
Regex_to_Remove_XML_item('{*}AgencyCode', r"^(?=.*ED).*$")
Regex_to_Remove_XML_item('{*}AgencyCode', r"^(?=.*DOE).*$")
Regex_to_Remove_XML_item('{*}AgencyCode', r"^(?=.*PAMS).*$")
Regex_to_Remove_XML_item('{*}AgencyCode', r"^(?=.*USDA).*$")
"""


"""
for oppSyn in root.findall('{*}OpportunitySynopsisDetail_1_0'):
    for otherCat in oppSyn.findall('{*}AdditionalInformationOnEligibility'):
        if re.search(r"(?=.*\beligibility is limited to\b).*$", str(otherCat.text), flags=re.I):
            root.remove(oppSyn)

for oppSyn in root.findall('{*}OpportunitySynopsisDetail_1_0'):
    for otherCat in oppSyn.findall('{*}AdditionalInformationOnEligibility'):
        if re.search(r"(?=.*\beligible applicants are limited).*$", str(otherCat.text), flags=re.I):
            root.remove(oppSyn)

"""


tree.write('Output/IGrants-DB-v2-TESTING.xml', xml_declaration=True, encoding='UTF-8', method='xml')


