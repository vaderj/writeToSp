
from pprint import pprint
import json
import os
import feedparser
import pyodbc
import requests
from requests_negotiate_sspi import HttpNegotiateAuth

dbServer = "databaseServer"
databaseName = "databaseName"

siteCollectionUrl = "http://some.url"
rootSiteURL = siteCollectionUrl + "/"
listName = "listName"

listUrl = rootSiteURL + "_api/web/lists/getByTitle('" + listName + "')/items"

response = 0
digestResponse = 0

digetsURL = siteCollectionUrl + "_api/contextinfo"
userContextUrl = rootSiteURL + "_api/web/ensureuser" 

shortHeaders = {'Content-Type': 'application/json;odata=verbose', 'Accept' : "application/json;odata=verbose" }
currentUsername = os.environ["USERNAME"]

class Tables:
    hospTblName = "Hospitals" 
    mmContactsTblName = "mmHospitalContacts" 
    contactsTblName = "Contacts" 
    marketsTblName = "Markets" 
    regionsTblName = "Regions" 
    divisionsTblName = "Divisions" 

class Fields:
    hospFields = "[MarketId],[HospitalNumber],[HospitalName],[City],[State],[PostalCode]"
    mmContactsFields = "[HospitalNumber],[EmployeeNumber],[Title]"
    contactsFields = "[Name],[EmployeeNumber],[Email]"
    marketsFields = "[Id],[RegionId],[Name]"
    regionsFields = "[Id],[DivisionId],[Name]"
    divisionsFields = "[Id],[Name]"

class SQLCommands:
    hospSqlCommand = "select top 10000 " + Fields.hospFields + " from " + Tables.hospTblName + ";" 
    mmContactsSqlCommand = "select top 100000 " + Fields.mmContactsFields + " from " + Tables.mmContactsTblName + " WHERE [IsLeader]=1; " 
    contactsSqlCommand = "select top 100000 " + Fields.contactsFields + " from " + Tables.contactsTblName + "; " 
    marketsSqlCommand = "select top 5000 " + Fields.marketsFields + " from " + Tables.marketsTblName + "; " 
    regionsSqlCommand = "select top 5000 " + Fields.regionsFields + " from " + Tables.regionsTblName + "; " 
    divisionsSqlCommand = "select top 5000 " + Fields.divisionsFields + " from " + Tables.divisionsTblName + "; " 

def querySql(server, dbname, query):
    cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
        "Server=" + server +";"
        "Database="+ dbname + ";"
        "Trusted_Connection=yes;")
    cursor = cnxn.cursor()
    cursor.execute(query)
    for row in cursor:
        print('row = %r' % (row,))

def getDigestRequest(url):
    res = requests.post(url,headers=shortHeaders ,auth=HttpNegotiateAuth(),verify=False)
    #digest = json.loads(res.content.decode('utf-8')).find("{http://schemas.microsoft.com/ado/2007/08/dataservices}FormDigestValue").text
    digest = json.loads(res.content.decode('utf-8'))
    return digest["d"]["GetContextWebInformation"]["FormDigestValue"]

def getSPcontext(url,username,digest):
    ctxHeaders = {'Content-Type': 'application/json;odata=verbose', 'Accept' : "application/json;odata=verbose", "X-RequestDigest":digest }
    payload = {'logonName': username, }
    context = requests.post(userContextUrl,data=json.dumps(payload),headers=ctxHeaders ,auth=HttpNegotiateAuth(),verify=False)
    return context


    
requestDigest = getDigestRequest(digetsURL)
ensureUser = getSPcontext(userContextUrl,currentUsername,requestDigest)

listItemResponse =  requests.get(listUrl,headers=shortHeaders ,auth=HttpNegotiateAuth(),verify=False)


print(json.loads(ensureUser.content.decode('utf-8'))["d"]["Email"])
