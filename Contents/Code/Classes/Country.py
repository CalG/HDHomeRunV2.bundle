# plex
from PMS import Prefs

class Country:
    def __init__(self, countryObj=None, abbrev=None, name=None):
        if countryObj:
            abbrev = countryObj['abbrev']
            name = countryObj['name']
  
        self.abbrev = abbrev
        self.name = name
  
    ########################################
    def fullName(self):
        return "%s (%s)" % (self.name, self.abbrev)
  
    ########################################
    def isDefault(self):
        return self.fullName() == Prefs.Get('country')
