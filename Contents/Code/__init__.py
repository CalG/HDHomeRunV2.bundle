# PMS plugin framework
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

from Code.Classes import CountryList
from Code.Classes.LineupList import LineupList
from Code.Classes import Lineup
from Code.Classes import Channel

########################################

VIDEO_PREFIX = "/video/hdhomerun"

NAME = L('Title')

ART           = 'art-default.png'
ICON          = 'icon-default.png'

DEFAULT_WATCH_CHANNEL_ICON = 'watch-channel.png'
WATCH_CHANNEL_ICON_LIST = [
    'watch-channel.png',
    'watch-abc.png',
    'watch-cbs.png',
    'watch-fox.png',
    'watch-nbc.png',
    'watch-pbs.png',
    'watch-cw.png',
    ]

SETTINGS_ICON = 'settings.png'
EDIT_CHANNELS_ICON = 'edit-channels.png'
DOWNLOAD_CHANNELS_ICON = 'download-channels.png'
ADD_URL_ICON = 'add-url.png'
EXPLORE_CHANNEL_ICON = 'toolbox.png'
ADD_CHANNEL_ICON = 'add-channel.png'
REMOVE_CHANNEL_ICON = 'remove-channel.png'
CHANGE_NAME_ICON = 'change-name.png'
CHANGE_IMAGE_ICON = 'change-icon.png'
DETAILS_ICON = 'details.png'

LINEUP_ANTENNA_ICON = 'lineup-antenna.png'
LINEUP_SATELLITE_ICON = 'lineup-satellite.png'
LINEUP_CABLE_ICON = 'lineup-cable.png'
LINEUP_COAX_ICON = 'lineup-coax.png'

# Preference Ids
DEVICE_ID = 'deviceId'
TUNER_ID = 'tunerId'
COUNTRY = 'country'
POSTAL_CODE = 'postalCode'

# Key for maing data structure stored in Dict
LINEUP_LIST = 'LineupList'

# For testing and debugging
CLEAR_LINEUP_LIST = False
FAST_MY_CHANNEL_ENTRY = False

# To control two approaches for unresolved icon caching issue
USE_VIDEO_ITEM_CALLBACKS = False

########################################
def Start():

    Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, L('VideoTitle'), ICON, ART)

    Plugin.AddViewGroup("MainList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("ExploreLineupList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("ExploreChannelList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("ExploreOptionsList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("ShowChannelImages", viewMode="InfoList", mediaType="items")

    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    MediaContainer.nocache = 1
    DirectoryItem.thumb = R(ICON)

    # (for testing)
    if CLEAR_LINEUP_LIST:
        Dict.Set(LINEUP_LIST, [] )
    
########################################
def CreatePrefs():
    Log( "Creating preferences ...", True )
    
    Prefs.Add( id=DEVICE_ID,
               type='text',
               default='',
               label=L('DeviceIdPrefLabel'))

    Prefs.Add( id=TUNER_ID,
               type='enum',
               default='0',
               label=L('TunerIdPrefLabel'),
               values='0|1|')
    
    Prefs.Add( id=COUNTRY,
               type='enum',
               default=L('CoutryPrefDefault'),
               label=L('CountryPrefLabel'),
               values=CountryList.toOptions())
    
    Prefs.Add( id=POSTAL_CODE,
               type='text',
               default='',
               label=L('PostalCodePrefLabel'))
 
########################################
def ValidatePrefs():
    msgList = getPreferencesErrorList()
    if len(msgList) < 1:
        return MessageContainer(
            L('Success'),
            L('SettingsSaved')
            )
    else:
        return MessageContainer(
            L('Error'),
            ' '.join( msgList )
        )

########################################
def getPreferencesErrorList():
    deviceId = Prefs.Get(DEVICE_ID)
    country = Prefs.Get(COUNTRY)
    postal_code = Prefs.Get(POSTAL_CODE)

    msgList = []
    if not deviceId:
        msgList.append( L('NoDeviceId'))
    if not country:
        msgList.append( L('NoCountry'))
    if not postal_code:
        msgList.append( L('NoPostalCode'))

    return msgList

########################################
def VideoMainMenu():
    dir = MediaContainer(viewGroup="MainList", noCache=True)

    AddActiveChannelItems( dir )
    AddExploreLineupsItem( dir )
    AddDownloadLineupsItem( dir )
    AddInsertChannelStream( dir )
       
    dir.Append( PrefsItem(
        title = L('PreferencesTitle'),
        subtile = L('PreferencesSubtitle'),
        summary =  L('PreferencesSummary'),
        thumb=R(SETTINGS_ICON)
        ))

    return dir

########################################
def AddActiveChannelItems( dir ):
    lineupList = Dict.Get(LINEUP_LIST)
    if not lineupList:
        return
    for lineup in lineupList:
        for channel in lineup.channelList:
            if not channel.isActive():
                continue
            AddVideoItem( dir,
                          lineup.getId(),
                          channel,
                          "%s %s" % ( L('Watch'), channel.getTitle() ),
                          subtitle=channel.getSubtitle(),
                          summary=channel.Resolution )

########################################
def AddVideoItem( dir, lineupId, channel, title, subtitle, summary ):
    streamUrl = GetStreamUrl( channel )
    if not streamUrl:
        return
    if USE_VIDEO_ITEM_CALLBACKS:
        dir.Append( Function(
            VideoItem( PlayStreamCallback,
                       title,
                       subtitle=subtitle,
                       summary=summary,
                       thumb=R(GetChannelImageName(channel)),
                       art=R(ART)
                       ),
            lineupId=lineupId,
            channelId=channel.getId() ))
    else:
        dir.Append( VideoItem( streamUrl,
                               title,
                               subtitle=subtitle,
                               summary=summary,
                               thumb=R(GetChannelImageName(channel)),
                               art=R(ART)
                               ))

########################################
def GetStreamUrl( channel ):
    if not channel:
        return None
    deviceId = Prefs.Get(DEVICE_ID)
    if not deviceId:
        return None
    tunerId = Prefs.Get(TUNER_ID)
    if not tunerId:
        tunerId = '0'
    return channel.getStreamUrl( deviceId, tunerId )
    
########################################
def AddExploreLineupsItem( dir ):
    lineupList = Dict.Get(LINEUP_LIST)
    if not lineupList:
        return
    dir.Append( Function(
        DirectoryItem( ExploreLineupsCallback,
                       L('ExploreChannels'),
                       summary=L('ExploreChannelsSummary'),
                       thumb=R(EDIT_CHANNELS_ICON),
                       art=R(ART)
                       )
        ))

########################################
def AddDownloadLineupsItem( dir ):
    country = CountryList.findByFullName( Prefs.Get(COUNTRY))
    if not country:
        return
    postalCode = Prefs.Get(POSTAL_CODE)
    if not postalCode:
        return
    lineupList = Dict.Get(LINEUP_LIST)
    if not lineupList:
        downloadTitle = L('DownloadChannels')
    else:
        downloadTitle = L('ReDownloadChannels')
    dir.Append( Function(
        DirectoryItem( DownloadLineupsCallback,
                       downloadTitle,
                       summary=L('DownloadChannelsSummary'),
                       thumb=R(DOWNLOAD_CHANNELS_ICON),
                       art=R(ART)
                       )
        ))

########################################
def AddInsertChannelStream( dir ):
    dir.Append( Function(
        InputDirectoryItem( InsertChannelCallback,
                            L('InsertChannelTitle'),
                            L('InsertChannelPrompt'),
                            subtitle=L('InsertChannelSubtitle'),
                            summary=L('InsertChannelSummary'),
                            thumb=R(ADD_URL_ICON),
                            art=R(ART),
                            )
        ))
   
########################################
def PlayStreamCallback(sender, lineupId, channelId ):
    channel = GetChannelById( lineupId, channelId )
    if not channel:
        return MessageContainer(
            L('Error'),
            L('NoChannelDataFound')
            )
    try:
        streamUrl = GetStreamUrl(channel )
        if not streamUrl:
            return MessageContainer(
                L('Error'),
                L('NoDeviceId')
                )
           
        #return Redirect( VideoItem( streamUrl, channel.getTitle() ))
        return streamUrl

    except Exception, e:
        Log( "Exception: %s" % e, False )
        return MessageContainer(
            L('Error'),
            "%s %s" % ( L('ProblemViewingChannel'), channel.getTitle() )
            )

########################################
def ExploreLineupsCallback(sender):
    lineupList = Dict.Get(LINEUP_LIST)
    if not lineupList:
        return MessageContainer(
            L('Error'),
            L('NoChannels')
            )

    dir = MediaContainer(viewGroup="ExploreLineupList", noCache=True)

    for lineup in lineupList:
        if len(lineup.channelList) < 1:
            continue
        dir.Append( Function(
            DirectoryItem( ExploreChannelsCallback,
                           lineup.getTitle(),
                           subtitle=lineup.getSubtitle(),
                           summary=lineup.getSummary(),
                           thumb=R(GetLineupImageName(lineup)),
                           art=R(ART)
                           ),
            lineupId=lineup.getId() ))

    return dir

########################################
def ExploreChannelsCallback(sender, lineupId):
    lineup = GetLineupById( lineupId )
    if not lineup:
        return MessageContainer(
            L('Error'),
            "%s (%s)" % ( L('NoLineupDataFound'), lineupId )
            )

    if len(lineup.channelList) < 1:
        return MessageContainer(
            L('NoChannels'),
            "%s %s" % ( L('NoChannelsFoundFor'), lineup.getTitle() )
            )

    dir = MediaContainer(viewGroup="ExploreChannelList", noCache=True)

    for channel in lineup.channelList:
        if not channel.isVerified():
            title = "%s (%s)" % ( channel.getTitle(), L('NotVerifiedState'))
        else:
            if channel.isEnabled():
                title = channel.getTitle()
            else:
                title = "%s (%s)" % ( channel.getTitle(), L('DisabledState'))
                
        dir.Append( Function(
            DirectoryItem( ExploreOptionsCallback,
                                title,
                                subtitle=channel.getSubtitle(),
                                summary=channel.getSummary(),
                                thumb=R(EXPLORE_CHANNEL_ICON),
                                art=R(ART)
                                ),
            lineupId=lineup.getId(),
            channelId=channel.getId() ))
        
    return dir

########################################
def ExploreOptionsCallback(sender, lineupId, channelId):
    channel = GetChannelById( lineupId, channelId )
    if not channel:
        return MessageContainer(
            L('Error'),
            L('NoChannelDataFound')
            )
    
    dir = MediaContainer(viewGroup="ExploreOptionsList", noCache=True)

    AddVideoItem( dir,
                  lineupId,
                  channel,
                  "%s %s" % ( L('TryToView'), channel.getTitle() ),
                  subtitle=channel.getSummary(),
                  summary=L('TryToViewSummary'))
    
    if not channel.isVerified():
        dir.Append( Function(
            DirectoryItem( VerifyChannelCallback,
                           "%s %s" % ( L('VerifyAndEnable'), channel.getTitle() ),
                           subtitle=channel.getSummary(),
                           summary=L('VerifyAndEnableSummary'),
                           thumb=R(ADD_CHANNEL_ICON),
                           art=R(ART)
                           ),
            lineupId=lineupId,
            channelId=channel.getId(),
            enabled=True))
        dir.Append( Function(
            DirectoryItem( VerifyChannelCallback,
                           "%s %s" % ( L('VerifyAndDisable'), channel.getTitle() ),
                           subtitle=channel.getSummary(),
                           summary=L('VerifyAndDisableSummary'),
                           thumb=R(REMOVE_CHANNEL_ICON),
                           art=R(ART)
                           ),
            lineupId=lineupId,
            channelId=channel.getId(),
            enabled=False))

    else:
        if channel.isEnabled():
            dir.Append( Function(
                DirectoryItem( EnableDisableCallback,
                               "%s %s" % ( L('Disable'), channel.getTitle() ),
                               subtitle=channel.getSummary(),
                               summary=L('DisableSummary'),
                               thumb=R(REMOVE_CHANNEL_ICON),
                               art=R(ART)
                               ),
                lineupId=lineupId,
                channelId=channel.getId(),
                enabled=False ))
        else:
            dir.Append( Function(
                DirectoryItem( EnableDisableCallback,
                               "%s %s" % ( L('Enable'), channel.getTitle() ),
                               subtitle=channel.getSummary(),
                               summary=L('EnableSummary'),
                               thumb=R(ADD_CHANNEL_ICON),
                               art=R(ART)
                               ),
                lineupId=lineupId,
                channelId=channel.getId(),
                enabled=True ))
    
    dir.Append( Function(
        InputDirectoryItem( SetChannelDisplayNameCallback,
                            "%s %s" % ( L('ChangeDisplayNameTitle'), channel.getTitle() ),
                            L('ChangeDisplayNamePrompt'),
                            subtitle=channel.getSummary(),
                            summary=L('ChangeDisplayNameSummary'),
                            thumb=R(CHANGE_NAME_ICON),
                            art=R(ART),
                            ),
        lineupId=lineupId,
        channelId=channel.getId(),
        ))

    dir.Append( Function(
        DirectoryItem( ShowChannelImageChoicesCallback,
                       "%s %s" % ( L('ChangeImageNameTitle'), channel.getTitle() ),
                       subtitle=channel.getSummary(),
                       summary=L('ChangeImageNameSummary'),
                       thumb=R(CHANGE_IMAGE_ICON),
                       art=R(ART),
                       ),
        lineupId=lineupId,
        channelId=channel.getId(),
        ))

    dir.Append( Function(
        DirectoryItem( ChannelDetailsCallback,
                       "%s %s" % ( L('SeeDetailsFor'), channel.getTitle() ),
                       subtitle=channel.getSummary(),
                       summary=L('SeeDetailsForSummary'),
                       thumb=R(DETAILS_ICON),
                       art=R(ART)
                       ),
        lineupId=lineupId,
        channelId=channel.getId() ))
    
    return dir
    
########################################
def VerifyChannelCallback(sender, lineupId, channelId, enabled):
    channel = GetChannelById( lineupId, channelId )
    if not channel:
        return MessageContainer(
            L('Error'),
            L('NoChannelDataFound')
            )

    channel.Verified = True
    channel.Enabled = enabled
    try:
        ReplaceChannelData(lineupId, channel)
    except Exception, e:
        Log( "Exception: %s" % e, False )
        return MessageContainer(
            L('Error'),
            "%s %s" % ( L('ProblemUpdatingChannels'), channel.getTitle() )
            )
    
    return MessageContainer(
        L('Success'),
        "%s %s" % ( channel.getTitle(), L('NowVerified') )
        )

########################################
def EnableDisableCallback(sender, lineupId, channelId, enabled): 
    channel = GetChannelById( lineupId, channelId )
    if not channel:
        return MessageContainer(
            L('Error'),
            L('NoChannelDataFound')
            )

    channel.Enabled = enabled
    try:
        ReplaceChannelData(lineupId, channel)
    except Exception, e:
        Log( "Exception: %s" % e, False )
        return MessageContainer(
            L('Error'),
            "%s %s" % ( L('ProblemUpdatingChannels'), channel.getTitle() )
            )
    if enabled:
        msg = L('NowEnabled')
    else:
        msg = L('NowDisabled')
    return MessageContainer(
        L('Success'),
        "%s %s" % ( channel.getTitle(), msg )
        )
        
########################################
def ChannelDetailsCallback(sender, lineupId, channelId):
    channel = GetChannelById( lineupId, channelId )
    if not channel:
        return MessageContainer(
            L('Error'),
            L('NoChannelDataFound')
            )

    return MessageContainer(
        L('ChannelDetails'),
        channel.toString()
        )
        
########################################
def DownloadLineupsCallback(sender):

    country = CountryList.findByFullName( Prefs.Get(COUNTRY))
    postalCode = Prefs.Get(POSTAL_CODE)

    if not country or not postalCode:
        return MessageContainer( L('NoLocationData'),
                                 L('SetYourLocationData') )

    try:
        lineupList = LineupList( country, postalCode )
    except Exception, e:
        Log( "Exception: %s" % e, False )
        return MessageContainer(
            L('Error'),
            "%s %s:%s " % ( L('ProblemFetchingChannels'),
                            country.abbrev, postalCode )
            )
    
    if len(lineupList) < 1:
        return MessageContainer(
            L('NoChannels'),
            "%s %s:%s" % ( L('NoChannelsFOundFor'),
                           country.abbrev, postalCode )
            )

    try:
        UpdateLineupList(lineupList)
    except Exception, e:
        Log( "Exception: %s" % e, False )
        return MessageContainer(
            L('Error'),
            "%s %s:%s " % ( L('ProblemUpdatingChannels'),
                            country.abbrev, postalCode )
            )

    return MessageContainer(
        L('Success'),
        "%d %s" % ( lineupList.getNumChannels(), L('ChannelsFound') )
        )

########################################
def InsertChannelCallback( sender, query ):

    # For testing by reducing url typing
    if FAST_MY_CHANNEL_ENTRY:
        # query = "hdhomerun://DEVICE-0/tuner0?channel=8vsb:999999&program=%s" % query
        query = "hdhomerun://DEVICE-0/ch24-%s" % query
    
    try:
        myChannel = Channel.fromUrl( query )
        if not myChannel:
            deviceId = Prefs.Get(DEVICE_ID)
            tunerId = Prefs.Get(TUNER_ID)

            return MessageContainer(
                L('Error'),
                "%s\n%s" % ( L('BadStreamUrl'),
                           "\n".join( Channel.getStreamUrlTemplates(deviceId, tunerId)))
                )

        # default channel to verfied and enabled
        myChannel.GuideName = L('MyChannel')
        myChannel.Verified = True
        myChannel.Enabled = True

        myLineupList = NewMyLineupList( myChannel )
        UpdateLineupList( myLineupList )
        
        return MessageContainer(
            L('Success'),
            "%s: %s" % ( L('Added'), myChannel.toString() )
            )

    except Exception, e:
        Log( "Exception: %s" % e, False )
        return MessageContainer(
            L('Error'),
            "%s: %s" % ( L('ProblemInsertingChannel'), query )
            )

########################################
def SetChannelDisplayNameCallback( sender, lineupId, channelId, query ):
    channel = GetChannelById( lineupId, channelId )
    if not channel:
        return MessageContainer(
            L('Error'),
            L('NoChannelDataFound')
            )

    channel.DisplayName = query
    try:
        ReplaceChannelData(lineupId, channel)
    except Exception, e:
        Log( "Exception: %s" % e, False )
        return MessageContainer(
            L('Error'),
            "%s %s" % ( L('ProblemSettingDisplayName'), channel.getTitle() )
            )

    return MessageContainer(
        L('Success'),
        "%s %s" % ( L('DisplayNameSetFor'), channel.getTitle() )
        )

########################################
def ShowChannelImageChoicesCallback( sender, lineupId, channelId ):
    channel = GetChannelById( lineupId, channelId )
    if not channel:
        return MessageContainer(
            L('Error'),
            L('NoChannelDataFound')
            )

    dir = MediaContainer(viewGroup="ShowChannelImages", noCache=True)

    for imageName in WATCH_CHANNEL_ICON_LIST:
        if channel.IconImageName == imageName:
            title = "%s (current)" % imageName
        else:
            title = imageName
        dir.Append( Function(
            DirectoryItem( SetChannelImageNameCallback,
                           title,
                           subtitle='',
                           summary='',
                           thumb=R(imageName),
                           art=R(ART)
                           ),
            lineupId=lineupId,
            channelId=channel.getId(),
            imageName=imageName ))
        
    return dir

########################################
def SetChannelImageNameCallback( sender, lineupId, channelId, imageName ):
    channel = GetChannelById( lineupId, channelId )
    if not channel:
        return MessageContainer(
            L('Error'),
            L('NoChannelDataFound')
            )

    channel.IconImageName = imageName
    try:
        ReplaceChannelData(lineupId, channel)
    except Exception, e:
        Log( "Exception: %s" % e, False )
        return MessageContainer(
            L('Error'),
            "%s %s" % ( L('ProblemSettingImageName'), channel.getTitle() )
            )

    return MessageContainer(
        L('Success'),
        "%s %s" % ( L('ImageNameSetFor'), channel.getTitle() )
        )

########################################
def ReplaceChannelData( lineupId, newChannel):
    if not newChannel:
        return
    lineupList = Dict.Get(LINEUP_LIST)
    if not lineupList:
        return
    lineupList.replaceChannel( lineupId, newChannel )
    Dict.Set(LINEUP_LIST, lineupList )

########################################
def UpdateLineupList( updatedLineupList ):
    if not updatedLineupList:
        return
    lineupList = Dict.Get(LINEUP_LIST)
    if not lineupList:
        Dict.Set(LINEUP_LIST, updatedLineupList )
        return
    lineupList.update( updatedLineupList )
    Dict.Set(LINEUP_LIST, lineupList )
    
########################################
def GetLineupById( lineupId ):
    lineupList = Dict.Get(LINEUP_LIST)
    if not lineupList:
        return None
    return lineupList.getLineup( lineupId )

########################################
def GetChannelById( lineupId, channelId ):
    lineup = GetLineupById( lineupId )
    if not lineup:
        return None
    return lineup.getChannel( channelId )

########################################
def NewMyLineupList( channel ):
    lineupList = []
    lineupList.append( Lineup.getMyLineup( channel ))
    return lineupList

########################################
def GetChannelImageName( channel ):
    iconImageName = channel.getIconImageName()
    if iconImageName:
        return iconImageName
    return DEFAULT_WATCH_CHANNEL_ICON

########################################
def GetLineupImageName( lineup ):
    iconImageName = lineup.getIconImageName()
    if iconImageName:
        return iconImageName
    if lineup.getTitle().lower().find( 'antenna') >= 0:
        return LINEUP_ANTENNA_ICON
    if lineup.getTitle().lower().find( 'satellite') >= 0:
        return LINEUP_SATELLITE_ICON
    if lineup.getTitle().lower().find( 'cable') >= 0:
        return LINEUP_CABLE_ICON
    return LINEUP_COAX_ICON
