# PMS plugin framework
#from PMS import XML
#from PMS import Log
#from PMS.Shortcuts import *

# plugin
#from Code import Util
#from Code.Classes import Lineup
import Util
import Lineup

class lineupList(list):
    """
    A list of all channel lineups
    """

    ########################################
    def __init__(self, country, postalCode):
        """
        Load the lineup list for a specific country/postalcode from
        SiliconDust website
        """
        self.country = country
        self.postalCode = postalCode
        self.loadLineups(country, postalCode)
    """
    def __getstate__(self):
        result = self.__dict__.copy()
        return result
    def __setstate__(self, dict):
        self.__dict__ = dict
	"""
    ########################################
    def loadLineups(self, country, postalCode):
        """
        Fetch lineup/channel data from silicondust.com and generate a list
        of Lineup objects. XML structure is:

        <LineupUIResponse>
            <Location>US:78750</Location>
           <Lineup>
              <DisplayName>Digital Antenna: Austin, TX, 78750</DisplayName>
              <DatabaseID>2252478</DatabaseID>
              <Program>
                   ... channel info
              </Program>
            </Lineup>
        </LineupUIResponse>
        """

        lineupUrl = 'http://www.silicondust.com/hdhomerun/lineup_web/%s:%s' % ( country.abbrev, postalCode )
        Log( "LOAD LINEUPS URL: %s" % lineupUrl )

        responseXml = XML.ElementFromURL( lineupUrl )
        
        location = Util.XPathSelectOne( responseXml,
                                        '/LineupUIResponse/Location')
        Log( "LOCATION %s" % location )

        for lineupItemXml in responseXml.xpath('/LineupUIResponse/Lineup'):
            lineup = Lineup.fromXml( lineupItemXml )
            self.append( lineup )

    ########################################
    def getNumChannels( self ):
        count = 0
        for lineup in self:
            count += lineup.getNumChannels()
        return count
    
    ########################################
    def getLineupIdx( self, lineupId ):
        for lineupIdx in xrange(len(self)):
            if self[lineupIdx].getId() == lineupId:
                return lineupIdx
        return -1
    
    ########################################
    def getLineup( self, lineupId ):
        lineupIdx = self.getLineupIdx( lineupId )
        if lineupIdx < 0:
            return None
        return self[lineupIdx]
    
    ########################################
    def update(self, updatedLineupList):

        for updatedLineup in updatedLineupList:
            lineupIdx = self.getLineupIdx( updatedLineup.getId() )
            if lineupIdx < 0:
                self.append( updatedLineup )
            else:
                self[lineupIdx].update( updatedLineup )

    ########################################
    def replaceChannel(self, lineupId, newChannel):

        lineupIdx = self.getLineupIdx( lineupId )

        # Do nothing if the new newChannelLineup does not exist since this
        # routine is only for replacing existing data.
        if lineupIdx < 0:
            return
        
        self[lineupIdx].replaceChannel( newChannel )
