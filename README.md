IGrants_XML_Trimmer

This script is my first attempt at writing Python code. (Frankly, I'm a bit surprised that it works.)

This script removes *most* non-international grants from the grants.gov downloadable XML database (download from here: https://www.grants.gov/web/grants/xml-extract.html) and reformats due dates & currency for readability, removes garbage opportunities (i.e., the "this is a test, do not apply" opps), adds hyperlinks to opportunity numbers (OppNums), and outputs two files; an XML file for use in an HTML table on our internal USA grants website and a CSV file to add new grants to a Google calendar.

Updated for Grants.gov v2.0 XML on 2017.01.02 
・ 2017.08.23 - now on github

