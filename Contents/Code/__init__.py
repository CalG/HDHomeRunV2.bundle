# PMS plugin framework
#from PMS import *
#from PMS.Objects import *
#from PMS.Shortcuts import *

#from Code.Classes import CountryList
#from Code.Classes.lineup_List import lineup_List
#from Code.Classes import Lineup
#from Code.Classes import Channel
import CountryList
import lineupList
from LineupList import lineupList
import Lineup
import Channel

########################################

VIDEO_PREFIX = "/video/hdhomerunV2"

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

#TODO Modify Prefs to the new json way.
# Preference Ids
device_id = 'deviceId'
tuner_id = 'tunerId'
country = 'country'
postal_code = 'postalCode'

# Key for maing data structure stored in Dict
KEY_LINEUP_LIST = 'key_lineup_List'

# For testing and debugging
CLEAR_LINEUP_LIST = False
FAST_MY_CHANNEL_ENTRY = False

# To control two approaches for unresolved icon caching issue
USE_VIDEO_ITEM_CALLBACKS = True

########################################
def Start():

    #Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, L('VideoTitle'), ICON, ART)

    Plugin.AddViewGroup("MainList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("ExploreLineupList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("ExploreChannelList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("ExploreOptionsList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("ShowChannelImages", viewMode="InfoList", mediaType="items")

#    ObjectContainer.art = R(ART)
#    ObjectContainer.title1 = NAME
#   ObjectContainer.nocache = 1
    ObjectContainer.art = R(ART)
    ObjectContainer.title1 = NAME
    ObjectContainer.no_cache = True

    DirectoryObject.thumb = R(ICON)

    # (for testing)
    if CLEAR_LINEUP_LIST:
        Dict[KEY_LINEUP_LIST] = []
    
########################################
def CreatePrefs():
    Log( "Creating preferences ...", True )
    
    Prefs.Add( id=device_id,
               type='text',
               default='',
               label=L('DeviceIdPrefLabel'))

    Prefs.Add( id=tuner_id,
               type='enum',
               default='0',
               label=L('TunerIdPrefLabel'),
               values='0|1|')
    
    Prefs.Add( id=country,
               type='enum',
               default=L('CoutryPrefDefault'),
               label=L('CountryPrefLabel'),
               values=CountryList.toOptions())
    
    Prefs.Add( id=postal_code,
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
    deviceId = Prefs['device_id']
    country = Prefs['country']
    postal_code = Prefs['postal_code']

	
    msgList = []
    if not deviceId:
        msgList.append( L('NoDeviceId'))
    if not country:
        msgList.append( L('NoCountry'))
    if not postal_code:
        msgList.append( L('NoPostalCode'))

    return msgList

########################################
@handler(VIDEO_PREFIX, L('VideoTitle'), ICON, ART)
def VideoMainMenu():
    dir = ObjectContainer(view_group="MainList", no_cache=True)
     
    # Add "Watch  channel.getTitle" if any active channels 
    AddActiveChannelItems( dir )
    
    # add L('ExploreChannels') "Verify and Edit Channel Data" menu option if there are any channels
    AddExploreLineupsItem( dir )
    
    # add Download channels" or "ReDownloadChannels"
    AddDownloadLineupsItem( dir )
    # add L('InsertChannelTitle') "Add Channel Stream" menu item
    AddInsertChannelStream( dir )
       
 #   dir.add( PrefsItem(
 #       title = L('PreferencesTitle'),
 #       summary =  L('PreferencesSummary'),
 #       thumb=R(SETTINGS_ICON)
 #       ))
    # add menu item to edit preferences.
    dir.add(PrefsObject (
                         title = L('PreferencesTitle'),
                         summary =  L('PreferencesSummary'),
                         thumb=R(SETTINGS_ICON)
                         )
            )

    dir.add(DirectoryObject(
                            key = Callback(DummyMenuItem),
                            title = "this is the title",
                            tagline = "tagline",
                            summary = "Summery",
                            thumb=R(SETTINGS_ICON)
                            )
            )
    return dir
########################################
def DummyMenuItem( ):
        return MessageContainer(
                                "you found me"
                               )
 
    
########################################
def AddActiveChannelItems( dir ):
    lineup_List = Dict[KEY_LINEUP_LIST]
    if not lineup_List:
        return
    for lineup in lineup_List:
        for channel in lineup.channelList:
            if not channel.isActive():
                continue
            AddVideoItem( dir,
                          lineup.getId(),
                          channel,
                          "%s %s" % ( L('Watch'), channel.getTitle() ),
                          summary=channel.Resolution )

########################################
#def AddVideoItem( dir, lineupId, channel, title, subtitle, summary ):
def AddVideoItem( dir, lineupId, channel, title, summary ):
    streamUrl = GetStreamUrl( channel )
    if not streamUrl:
        Log("AddVideoItem, no stream URL")
        return
    if USE_VIDEO_ITEM_CALLBACKS:
        dir.add(VideoClipObject( 
                                key = Callback(PlayStreamCallback,lineupId=lineupId, channelId=channel.getId() ),
                                rating_key = streamUrl,
                                title=title,
                                summary=summary,
                                thumb=R(GetChannelImageName(channel)),
                                art=R(ART)
                                )
                )
            
    else:
        dir.add(VideoClipObject( url = streamUrl,
                               title = title,
                               summary=summary,
                               thumb=R(GetChannelImageName(channel)),
                               art=R(ART)
                               )
                )

########################################
def GetStreamUrl( channel ):
    if not channel:
        return None
    deviceId = Prefs['device_id']
    if not deviceId:
        return None
    tunerId = Prefs['tuner_id']
    if not tunerId:
        tunerId = '0'
    return channel.getStreamUrl( deviceId, tunerId )
    
########################################
def AddExploreLineupsItem( dir ):
    lineup_List = Dict[KEY_LINEUP_LIST]
    if not lineup_List:
        return
    dir.add( DirectoryObject( 
                             key = Callback(ExploreLineupsCallback),
                             title = L('ExploreChannels'),
                             tagline = "tagline",
                             summary=L('ExploreChannelsSummary'),
                             thumb=R(EDIT_CHANNELS_ICON),
                             art=R(ART)
                            )
            )

########################################
def AddDownloadLineupsItem( dir ):
    country = CountryList.findByFullName(Prefs['country'])
	
    Log("AddDownloadLineupsItem.country :"+ Prefs['country'])
    if not country:
        return
    postalCode = Prefs['postal_code']
    if not postalCode:
        return
    lineup_List = Dict[KEY_LINEUP_LIST]
    if not lineup_List:
        downloadTitle = L('DownloadChannels')
    else:
        downloadTitle = L('ReDownloadChannels')
    dir.add( DirectoryObject( 
                       key = Callback(DownloadLineupsCallback),
                       title = downloadTitle,
                       tagline ="tagline",
                       summary=L('DownloadChannelsSummary'),
                       thumb=R(DOWNLOAD_CHANNELS_ICON),
                       art=R(ART)
                       )
        )

########################################
def AddInsertChannelStream( dir ):
    dir.add( InputDirectoryObject(
                            key = Callback(InsertChannelCallback),
                            title = L('InsertChannelTitle'),
                            prompt = L('InsertChannelPrompt'),
                            tagline = "tagline",
                            summary=L('InsertChannelSummary'),
                            thumb=R(ADD_URL_ICON),
                            art=R(ART),
                            )
        )
   
########################################
#def PlayStreamCallback(sender, lineupId, channelId ):
def PlayStreamCallback( lineupId, channelId ):
    # example on how to use VLC to transcode Live TV stream
	#http://forum.videolan.org/viewtopic.php?f=4&t=70404
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
        """
        Log("Redirecting %s" % streamUrl)
        #return Redirect( VideoItem( streamUrl, channel.getTitle() ))
        return Redirect(streamUrl)
		"""
        Log("Playing Stream %s" % streamUrl)
		
#        return VideoClipObject ( url = streamUrl,
#                                 title = channel.getTitle()
#                                )
#		 WindowsMediaVideoURL(url, width=None, height=None)
        return WindowsMediaVideoURL(streamUrl, width=None, height=None)
        """
		   Select a sub-program:
               hdhomerun_config FFFFFFFF set /tuner0/program 3
           Set the target:
               hdhomerun_config FFFFFFFF set /tuner0/target <ip address of pc>:5000
        """

 #       return MovieObject ( url = streamUrl,
 #                                title = channel.getTitle()
 #                               )
        #return streamUrl

    except Exception, e:
        #Log.Error( "Exception: %s" % e)
        Log.Error( "Exception: %s" % e )
        return MessageContainer(
            L('Error'),
            "%s %s" % ( L('ProblemViewingChannel'), channel.getTitle() )
            )

########################################
#def ExploreLineupsCallback(sender):
def ExploreLineupsCallback():
    lineup_List = Dict[KEY_LINEUP_LIST]
    if not lineup_List:
        return MessageContainer(
            L('Error'),
            L('NoChannels')
            )

    dir = ObjectContainer(view_group="ExploreLineupList", no_cache=True)

    for lineup in lineup_List:
        if len(lineup.channelList) < 1:
            continue
        dir.add( DirectoryObject( 
                           key = Callback(ExploreChannelsCallback, lineupId =lineup.getId()) ,
                           title = "%s (%s)" % (lineup.getTitle(), lineup.getSubtitle()),
                           tagline ="tagline",
                           summary=lineup.getSummary(),
                           thumb=R(GetLineupImageName(lineup)),
                           art=R(ART)
                           )
            )

    return dir

########################################
#def ExploreChannelsCallback(sender, lineupId):
def ExploreChannelsCallback(lineupId):
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

    dir = ObjectContainer(view_group="ExploreChannelList", no_cache=True)

    for channel in lineup.channelList:
        if not channel.isVerified():
            title = "%s (%s)" % ( channel.getTitle(), L('NotVerifiedState'))
        else:
            if channel.isEnabled():
                title = channel.getTitle()
            else:
                title = "%s (%s)" % ( channel.getTitle(), L('DisabledState'))
#        title = "%s (%s)" % ( channel.getTitle(), L('DisabledState'))
               
#        dir.Append( Function(
#            DirectoryObject( ExploreOptionsCallback,
#                                title,
#                                subtitle=channel.getSubtitle(),
#                                summary=channel.getSummary(),
#                                thumb=R(EXPLORE_CHANNEL_ICON),
#                                art=R(ART)
#                                ),
#            lineupId=lineup.getId(),
#            channelId=channel.getId() ))
        dir.add( DirectoryObject( 
                            key = Callback(ExploreOptionsCallback, lineupId=lineup.getId(), channelId=channel.getId()),
                            title = title,
                            tagline = "tagline",
                            summary=channel.getSummary(),
                            thumb=R(EXPLORE_CHANNEL_ICON),
                            art=R(ART)
                            )
             )
       
    return dir

########################################
#def ExploreOptionsCallback(sender, lineupId, channelId):
def ExploreOptionsCallback(lineupId, channelId):
    channel = GetChannelById( lineupId, channelId )
    if not channel:
        return MessageContainer(
            L('Error'),
            L('NoChannelDataFound')
            )
    
    dir = ObjectContainer(view_group="ExploreOptionsList", no_cache=True)

    AddVideoItem( dir,
                  lineupId,
                  channel,
                  "%s %s" % ( L('TryToView'), channel.getTitle() ),
                  summary=L('TryToViewSummary')
                )
    
    if not channel.isVerified():
        Log("building channel verification directory")
        dir.add(DirectoryObject(
                           key = Callback(VerifyChannelCallback,lineupId=lineupId, channelId=channel.getId(), enabled=True),
                           title = "%s %s" % ( L('VerifyAndEnable'), channel.getTitle() ),
                           tagline = "tagline",
                           summary=L('VerifyAndEnableSummary'),
                           thumb=R(ADD_CHANNEL_ICON),
                           art=R(ART)
                           )
                )
        dir.add(DirectoryObject(
                           key = Callback(VerifyChannelCallback,lineupId=lineupId, channelId=channel.getId(), enabled=False),
                           title = "%s %s" % ( L('VerifyAndDisable'), channel.getTitle() ),
                           tagline = "tagline",
                           summary=L('VerifyAndDisableSummary'),
                           thumb=R(REMOVE_CHANNEL_ICON),
                           art=R(ART)
                           )
                )

    else:
        if channel.isEnabled():
            dir.add( DirectoryObject(
                               key = Callback(EnableDisableCallback,lineupId=lineupId,channelId=channel.getId(),enabled=True),
                               title = "%s %s" % ( L('Disable'), channel.getTitle() ),
                               tagline = "tagline",
                               summary=L('DisableSummary'),
                               thumb=R(REMOVE_CHANNEL_ICON),
                               art=R(ART)
                               ) 
            )
        else:
            dir.add( DirectoryObject(
                               key = Callback(EnableDisableCallback,lineupId=lineupId,channelId=channel.getId(),enabled=True),
                               title = "%s %s" % ( L('Enable'), channel.getTitle() ),
                               summary=L('EnableSummary'),
                               tagline = "tagline",
                               thumb=R(ADD_CHANNEL_ICON),
                               art=R(ART)
                               )
                    )
    
    dir.add(InputDirectoryObject(
                            key = Callback(SetChannelDisplayNameCallback, lineupId=lineupId, channelId=channel.getId()),
                            title = "%s %s" % ( L('ChangeDisplayNameTitle'), channel.getTitle() ),
                            tagline = "tagline",
                            prompt = L('ChangeDisplayNamePrompt'),
                            summary=L('ChangeDisplayNameSummary'),
                            thumb=R(CHANGE_NAME_ICON),
                            art=R(ART),
                            )
            )

    dir.add(DirectoryObject( 
                       key = Callback(ShowChannelImageChoicesCallback, lineupId=lineupId, channelId=channel.getId()),
                       title = "%s %s" % ( L('ChangeImageNameTitle'), channel.getTitle() ),
                       summary=L('ChangeImageNameSummary'),
                       tagline = "tagline",
                       thumb=R(CHANGE_IMAGE_ICON),
                       art=R(ART),
                       )
            )

    dir.add( DirectoryObject(
                       key = Callback(ChannelDetailsCallback,lineupId=lineupId,channelId=channel.getId()),
                       title = "%s %s" % ( L('SeeDetailsFor'), channel.getTitle() ),
                       summary=L('SeeDetailsForSummary'),
                       tagline = "tagline",
                       thumb=R(DETAILS_ICON),
                       art=R(ART)
                       ) 
        )
    dir.add( DirectoryObject(
                       key = Callback(ChannelURLCallback,lineupId=lineupId,channelId=channel.getId()),
                       title = "%s %s" % ( "See URL", channel.getTitle() ),
                       summary=L('SeeDetailsForSummary'),
                       tagline = "tagline",
                       thumb=R(DETAILS_ICON),
                       art=R(ART)
                       ) 
        )
   
    return dir
    
########################################
#def VerifyChannelCallback(sender, lineupId, channelId, enabled):
def VerifyChannelCallback(lineupId, channelId, enabled):
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
        Log.Error( "Exception: %s" % e)
        return MessageContainer(
            L('Error'),
            "%s %s" % ( L('ProblemUpdatingChannels'), channel.getTitle() )
            )
    
    return MessageContainer(
        L('Success'),
        "%s %s" % ( channel.getTitle(), L('NowVerified') )
        )

########################################
#def EnableDisableCallback(sender, lineupId, channelId, enabled): 
def EnableDisableCallback(lineupId, channelId, enabled): 
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
        Log.Error( "Exception: %s" % e)
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
#def ChannelDetailsCallback(sender, lineupId, channelId):
def ChannelDetailsCallback(lineupId, channelId):
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
def ChannelURLCallback(lineupId, channelId):
    channel = GetChannelById( lineupId, channelId )
    streamUrl = GetStreamUrl( channel )
    return MessageContainer(
        L('ChannelDetails'),
        streamUrl
        )
        
########################################
#def DownloadLineupsCallback(sender):
def DownloadLineupsCallback():
    global lineup_List
    country = CountryList.findByFullName( Prefs['country'])
    postalCode = Prefs['postal_code']

    if not country or not postalCode:
        return MessageContainer( L('NoLocationData'),
                                 L('SetYourLocationData') )

    try:
#       Still cannot pickle, but info in now saved.
        lineup_List = lineupList( country, postalCode )
    except Exception, e:
        #Log.Error( "Exception: %s" % e)
        Log.Error( "Exception lineup_List: %s" % e)
        return MessageContainer(
            L('Error'),
            "%s %s:%s " % ( L('ProblemFetchingChannels'),
                            country.abbrev, postalCode )
            )
    
    if len(lineup_List) < 1:
        return MessageContainer(
            L('NoChannels'),
            "%s %s:%s" % ( L('NoChannelsFOundFor'),
                           country.abbrev, postalCode )
            )

    try:
        UpdateLineupList(lineup_List)
    except Exception, e:
        Log.Error( "Exception: %s" % e)
        return MessageContainer(
            L('Error'),
            "%s %s:%s " % ( L('ProblemUpdatingChannels'),
                            country.abbrev, postalCode )
            )

    return MessageContainer(
        L('Success'),
        "%d %s" % ( lineup_List.getNumChannels(), L('ChannelsFound') )
        )

########################################
#def InsertChannelCallback( sender, query ):
def InsertChannelCallback(query):

    # For testing by reducing url typing
    if FAST_MY_CHANNEL_ENTRY:
        # query = "hdhomerun://DEVICE-0/tuner0?channel=8vsb:999999&program=%s" % query
        query = "hdhomerun://DEVICE-0/ch24-%s" % query
    
    try:
        myChannel = Channel.fromUrl( query )
        if not myChannel:
            deviceId = Prefs['device_id']
            tunerId = Prefs['tuner_id']

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
        Log.Error( "Exception: %s" % e)
        return MessageContainer(
            L('Error'),
            "%s: %s" % ( L('ProblemInsertingChannel'), query )
            )

########################################
#def SetChannelDisplayNameCallback( sender, lineupId, channelId, query ):
def SetChannelDisplayNameCallback(lineupId, channelId, query ):
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
        Log.Error( "Exception: %s" % e)
        return MessageContainer(
            L('Error'),
            "%s %s" % ( L('ProblemSettingDisplayName'), channel.getTitle() )
            )

    return MessageContainer(
        L('Success'),
        "%s %s" % ( L('DisplayNameSetFor'), channel.getTitle() )
        )

########################################
#def ShowChannelImageChoicesCallback( sender, lineupId, channelId ):
def ShowChannelImageChoicesCallback(lineupId, channelId ):
    channel = GetChannelById( lineupId, channelId )
    if not channel:
        return MessageContainer(
            L('Error'),
            L('NoChannelDataFound')
            )

    dir = ObjectContainer(view_group="ShowChannelImages", no_cache=True)

    for imageName in WATCH_CHANNEL_ICON_LIST:
        if channel.IconImageName == imageName:
            title = "%s (current)" % imageName
        else:
            title = imageName
        dir.add(  DirectoryObject(
                           key = Callback(SetChannelImageNameCallback,lineupId=lineupId,channelId=channel.getId(),imageName=imageName),
                           title = title,
                           tagline = "tagline",
                           summary='',
                           thumb=R(imageName),
                           art=R(ART)
                           ) 
            )
        
    return dir

########################################
#def SetChannelImageNameCallback( sender, lineupId, channelId, imageName ):
def SetChannelImageNameCallback(lineupId, channelId, imageName ):
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
        Log.Error( "Exception: %s" % e)
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
    lineup_List = Dict[KEY_LINEUP_LIST]
    if not lineup_List:
        return
    lineup_List.replaceChannel( lineupId, newChannel )
    Dict[KEY_LINEUP_LIST]  =  lineup_List 

########################################
def UpdateLineupList( updatedLineupList ):
    if not updatedLineupList:
        return
    lineup_List = Dict[KEY_LINEUP_LIST]
    if not lineup_List:
        Dict[KEY_LINEUP_LIST] = updatedLineupList 
        return
    lineup_List.update( updatedLineupList )
    Dict[KEY_LINEUP_LIST]  =  lineup_List 
    
########################################
def GetLineupById( lineupId ):
    lineup_List = Dict[KEY_LINEUP_LIST]
    if not lineup_List:
        return None
    return lineup_List.getLineup( lineupId )

########################################
def GetChannelById( lineupId, channelId ):
    lineup = GetLineupById( lineupId )
    if not lineup:
        return None
    return lineup.getChannel( channelId )

########################################
def NewMyLineupList( channel ):
    lineup_List = []
    lineup_List.append( Lineup.getMyLineup( channel ))
    return lineup_List

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
