# Python libs
import re

# PMS plugin framework
from PMS.Shortcuts import *

# plugin
from Code import Util

########################################
class Channel:
    """
    Encapsulates all the information about a single channel or stream that
    the HDHomeRUn device can serve.
    """
    def __init__(self):
        # We make the attribute names match the XML tags
        self.Modulation = None
        self.Frequency = None
        self.PhysicalChannel = None
        self.ProgramNumber = None
        self.GuideNumber = None
        self.GuideName = None
        self.Resolution = None
        self.Aspect = None
        self.Snapshot = []

        # This data is manipulated by user
        self.Verified = False
        self.Enabled = False
        self.DisplayName = None
        self.IconImageName = None
        
    ########################################
    def getId(self):
        """
        We define uniqueness and equality by the stream url, or at least
        the portion that is indpenent of the device and tuner Ids
        """
        if self.Modulation and self.Frequency and self.ProgramNumber:
            return "%s:%s:%s" % ( self.Modulation,
                                  self.Frequency,
                                  self.ProgramNumber )
        if self.PhysicalChannel and self.ProgramNumber:
            return "%s:%s" % ( self.PhysicalChannel,
                               self.ProgramNumber )
        return self.toString()
    
    ########################################
    def equals(self, other):
        return self.getId() == other.getId()
    
    ########################################
    def isVerified(self):
        """
        This is set when the user verifies that the channel works.  Lots of
        data from the SiliconDust site might not be working or applicable.
        """
        return self.Verified

    ########################################
    def isEnabled(self):
        """
        If false, then even if the channel has been verfieid, it will not
        show up in the main channel list
        """
        return self.Enabled

    ########################################
    def isActive(self):
        """
        Active means the user has verified it to be a working channel
        and wants to include this in the main list of channels,
        """
        return self.Verified and self.Enabled

    ########################################
    def update(self, other):
        """
        Will update the channel fields that are allowed to change.
        Thus, it includes everything but:
          - those attributes that uniquely define the channel/stream
          - those attributes that the user sets
        """
        self.PhysicalChannel = other.PhysicalChannel
        self.GuideNumber = other.GuideNumber
        self.GuideName = other.GuideName
        self.Resolution = other.Resolution
        self.Aspect = other.Aspect
        self.Snapshot = other.Snapshot
        if other.DisplayName:
            self.DisplayName = other.DisplayName
        if other.IconImageName:
            self.IconImageName = other.IconImageName

    ########################################
    def getIconImageName(self):
        if self.IconImageName:
            return self.IconImageName
        return None
    
    ########################################
    def getTitle(self):
        if self.DisplayName:
            return self.DisplayName
        if self.GuideName:
            return self.GuideName
        return L('Unknown')
    
    ########################################
    def getSubtitle(self):
        if self.GuideNumber:
            return "%s %s" % ( L('Channel'), self.GuideNumber )
        if self.PhysicalChannel:
            return "%s %s" % ( L('Channel'), self.PhysicalChannel )
        return ''
    
    ########################################
    def getSummary(self):
        buff = []
        if self.GuideNumber:
            buff.append( self.GuideNumber )
        if self.Resolution:
            buff.append( self.Resolution )
        if self.Aspect:
            buff.append( self.Aspect )
        return ', '.join( buff )
    
    ########################################
    def getStreamUrl( self, deviceId, tunerId ):
        if self.Modulation and self.Frequency and self.ProgramNumber:
            return "hdhomerun://%s-%s/tuner%s?channel=%s:%s&program=%s" % ( deviceId, tunerId, tunerId, self.Modulation, self.Frequency, self.ProgramNumber )
        if self.PhysicalChannel and self.ProgramNumber:
            return "hdhomerun://%s-%s/ch%s-%s" % ( deviceId, tunerId, self.PhysicalChannel, self.ProgramNumber )
        return None
    
    ########################################
    def toString(self):
        """
        Note that we forego using the string bundle here, because we
        want these labels to match up with the XML tags.
        """
        buff = []
        buff.append( "Modulation = %s" % self.Modulation )
        buff.append( "Frequency = %s" % self.Frequency )
        buff.append( "PhysicalChannel = %s" % self.PhysicalChannel )
        buff.append( "ProgramNumber = %s" % self.ProgramNumber )
        buff.append( "GuideNumber = %s" % self.GuideNumber )
        buff.append( "GuideName = %s" % self.GuideName )
        buff.append( "Resolution = %s" % self.Resolution )
        buff.append( "Aspect = %s" % self.Aspect )
        return ", ".join( buff )
    
########################################
def fromXml( programXml ):
    """
    Parses a snippet of the XML returned from the SiliconDust site for a
    given country and postal code. The XML for a single channel looks like
    this:
    
    		<Program>
     		<Modulation>8vsb</Modulation>
    			<Frequency>479000000</Frequency>
    			<PhysicalChannel>15</PhysicalChannel>
    			<ProgramNumber>3</ProgramNumber>
    			<GuideNumber>25.1</GuideNumber>
    			<GuideName>KAVUDT</GuideName>
    			<Resolution>1280x720p</Resolution>
    			<Aspect>16:9</Aspect>
    			<Snapshot>19337181</Snapshot>
    			<Snapshot>19305855</Snapshot>
    			<Snapshot>19435334</Snapshot>
    		</Program>
    """
    
    channel = Channel()

    channel.Modulation = Util.XPathSelectOne(programXml, 'Modulation')
    channel.Frequency = Util.XPathSelectOne( programXml, 'Frequency')
    channel.PhysicalChannel = Util.XPathSelectOne( programXml, 'PhysicalChannel')
    channel.ProgramNumber = Util.XPathSelectOne( programXml, 'ProgramNumber')
    channel.GuideNumber = Util.XPathSelectOne( programXml, 'GuideNumber')
    channel.GuideName = Util.XPathSelectOne( programXml, 'GuideName')
    channel.Resolution = Util.XPathSelectOne( programXml, 'Resolution')
    channel.Aspect = Util.XPathSelectOne( programXml, 'Aspect')

    for snapshot in programXml.xpath('Snapshot'):
        channel.Snapshot.append( snapshot.text )

    return channel

########################################
def fromUrl( streamUrl ):
    """
    Two types of valid stream URLs:

    hdhomerun://<device-id>-<tuner>/ch<physical-channel>-<program-number>

    hdhomerun://<device-id>-<tuner>/tuner<tuner>?channel=<modulation>:<frequency>&program=<program-number>

    """

    channel = Channel()
    
    urlRe = re.compile( r'^\s*hdhomerun\:\/\/([\w\-]+)\-(\d+)\/tuner(\d+)\?channel\=([^\:]+)\:(.+)\&program\=(.+)$' )
    reMatch = urlRe.match( streamUrl )
    if reMatch:
        deviceId = reMatch.group(1)
        tunerId1 = reMatch.group(2)
        tunerId2 = reMatch.group(3)
        channel.Modulation = reMatch.group(4)
        channel.Frequency = reMatch.group(5)
        channel.ProgramNumber = reMatch.group(6)
        return channel

    urlRe = re.compile( r'^\s*hdhomerun\:\/\/([\w\-]+)\-(\d+)\/ch([^\-]+)-(\w+)$' )
    reMatch = urlRe.match( streamUrl )
    if reMatch:
        deviceId = reMatch.group(1)
        tunerId1 = reMatch.group(2)
        channel.PhysicalChannel = reMatch.group(3)
        channel.ProgramNumber = reMatch.group(4)
        return channel

    return None

########################################
def getStreamUrlTemplates( deviceId, tunerId ):
    templateUrls = []
    templateUrls.append( "hdhomerun://%s-%s/tuner%s?channel=<modulation>:<frequency>&program=<program-number>" % ( deviceId, tunerId, tunerId ))
    templateUrls.append( "hdhomerun://%s-%s/ch<physical-channel>-<program-number>" % ( deviceId, tunerId ))
    return templateUrls
    
