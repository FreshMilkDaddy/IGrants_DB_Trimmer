iGrants_Parser.py parses the XML extract from https://www.grants.gov/web/grants/xml-extract.html.
It's purpose is to extract NIH grants opening in 6 months (from the day the program is run) that are available to international applicants.
To use:
 - download an XML extract from the grants.gov webite above, 
 - delete the date in the filename so that it becomes "GrandsDBExtractv2.xml" and put the file in the "Data" folder,
 - create another folder called "Output",
 - run the program. (Obviously you will need to install any missing packages.)

The trimmed XML file (IGrants-DB-v2.xml) will be written to the Output folder. This can be used in a website to build a table of international grants.

Another file called "IGrants-Cal-v2.csv" will also be written. This file has the same information as the XML file and can be uploaded to a Google Calendar.

No guarantees are made. Use at your own risk.