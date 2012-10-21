# plex
#from PMS import Prefs

# plugin
#from Code.Classes.Country import Country
#from Code.Config import C
import Country
from Config import C

countries = []
for country in C["COUNTRIES"]:
    countries.append(Country.Country(country))

########################################
def defaultCountry():
    return findByFullName(Prefs['country'])

########################################
def findByFullName(fullName):
    Log.Info("findByFullName 10 :checking " + countries[10].fullName())
    for country in countries:
        #Log("findByFullName :checking " + country.fullName())
        if country.fullName() == fullName:
            return country

########################################
def findByAbbrev(abbrev):
    for country in countries:
        if str(country.abbrev) == str(abbrev):
            return country

			########################################
def findByIndex(index):
    return countries[indexx]

########################################
def toOptions():
    options = countries[:]
    options.reverse()
  
    values = '(None)|'
    for country in options:
        values += country.fullName() + '|'
    del options
  
    return values

