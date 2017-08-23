<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match = "/">

	<html>
	<body>
	<table border="1">
		<tr bgcolor="#89A533">
			<th>Fund Type</th>
			<th>Theme</th>
			<th>Title</th>
			<th>Number of Awards</th>
			<th>Estimated Funding (USD)</th>
			<th>Award Ceiling (USD)</th>
			<th>Award Floor (USD)</th>
			<th>Due Date (Y-m-d)</th>
			<th>Opp. Number</th>
		</tr>
		<xsl:for-each select="Grants/FundingOppSynopsis">
		<tr>
			<td align='center'><xsl:value-of select="FundingInstrumentType"/></td>
			<td align='center'><xsl:value-of select="FundingActivityCategory"/></td>
			<td><xsl:value-of select="FundingOppTitle"/></td>
			<td align='center'><xsl:value-of select="NumberOfAwards"/></td>
			<td align='center'><xsl:value-of select="EstimatedFunding"/></td>
			<td align='center'><xsl:value-of select="AwardCeiling"/></td>
			<td align='center'><xsl:value-of select="AwardFloor"/></td>
			<td align='center'><xsl:value-of select="ApplicationsDueDate"/></td>
			<td align='center'><xsl:value-of select="FundingOppNumber"/></td>
		</tr>
		</xsl:for-each>
		<xsl:for-each select="Grants/FundingOppModSynopsis">
		<tr>
			<td><xsl:value-of select="FundingInstrumentType"/></td>
			<td><xsl:value-of select="FundingActivityCategory"/></td>
			<td><xsl:value-of select="FundingOppTitle"/></td>
			<td><xsl:value-of select="NumberOfAwards"/></td>
			<td><xsl:value-of select="EstimatedFunding"/></td>
			<td><xsl:value-of select="AwardCeiling"/></td>
			<td><xsl:value-of select="AwardFloor"/></td>
			<td><xsl:value-of select="ApplicationsDueDate"/></td>
			<td><xsl:value-of select="FundingOppNumber"/></td>
		</tr>
		</xsl:for-each>
	</table>
	</body>
	</html>

</xsl:template>  
                                       
</xsl:stylesheet>
