# plex
from PMS import Prefs

# plugin
from Code.Classes.Country import Country
from Code.Config import C

countries = []
for country in C["COUNTRIES"]:
    countries.append(Country(country))

########################################
def defaultCountry():
    return findByFullName(Prefs.Get('country'))

########################################
def findByFullName(fullName):
    for country in countries:
        if country.fullName() == fullName:
            return country

########################################
def findByAbbrev(abbrev):
    for country in countries:
        if str(country.abbrev) == str(abbrev):
            return country

########################################
def toOptions():
    options = countries[:]
    options.reverse()
  
    values = '(None)|'
    for country in options:
        values += country.fullName() + '|'
    del options
  
    return values

