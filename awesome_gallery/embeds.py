#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import ssl
import json
from urllib import urlencode, quote, unquote
import urllib2 as urllib
from socket import timeout as TimeoutException
# from ssl import SSLError
import urlparse
import cgi
import requests
import xml.etree.ElementTree as ET
from django.conf import settings
from django.core.cache import cache
from httplib import BadStatusLine
 
# The domain allows for embed urls
WHITELIST_EMBED_PROVIDERS = [{'name': 'ustream\.tv'},
                             {'name': 'livestream\.com'},
                             {'name': 'nowthisnews\.com'},
                             {'name': 'tout\.com'},
                             {'name': 'kickstarter\.com'},
                             {'name': 'viddy\.com'},
                             {'name': 'slideshare\.net'},
                             {'name': 'nowthis(.)+\.akamaihd.net'},
                             {'name': 'kiwi\.ly'},
                             {'name': 'qwiki\.com'},
                             {'name': 'media\.mtvnservices\.com'},
                             {'name': 'mediamtvnserv(.)+\.akamaihd\.net'},
                             {'name': 'theonion\.com'},
                             {'name': 'facebook\.com'},
                             {'name': 'www\.reverbnation\.com'},
                             {'name': 'www\.flickr\.com'},
                             {'name': 'www\.snappytv\.com'},
                             {'name': 'events\.sap\.com'},
                             {'name': 'audioboo\.fm', 'height': True},
                             {'name': 'player\.ooyala\.com'},
                             {'name': 'www\.burst\.it'},
                             {'name': 'secure\.jtvnw\.net'},
                             {'name': 'vzaar\.com'}]  # justin.tv and twitch.tv
 
WHITELIST_EMBED_PROVIDERS_TESTING = ['cbsnews.com', 'video.msnbc.msn.com',
                                     'abcnews.go.com', '5min.com', 'brightcove\.com',
                                     'wordpress.tv', 'bandcamp.com', 'www.myspace.com']
 
 
class EmbedFactory:
 
    @staticmethod
    def get_embed(url, params=None):
        """Return an video just given the link"""
        if not url:
            return None
 
        embed_dict = []
        if type(url) == dict:
 
            # For those weird cases when og:video:type is declared but not og:video
            if not 'url' in url:
                return None
 
            #video_type = url.get('type')
            embed_dict = url
            url = url['url']
 
        url = url.strip()
 
        p = urlparse.urlparse(url)
        for embed_subclass in Embed.__subclasses__():
            if embed_subclass.check_url(parse_url=p):
                return embed_subclass(url, params=None)
        # if not was between subclass of EmbedResource
        if all(x in embed_dict for x in ['video', 'url']):
 
            # custom for new.livestream.com, clear iframe inside the url, and add w&h
            if 'iframe src=' in embed_dict['video']:
                embed_dict['video'] = EmbedFactory._livestream_clean(embed_dict['video'])
 
            embed_url = urlparse.urlparse(embed_dict['video'])
            for provider in WHITELIST_EMBED_PROVIDERS:
                if re.search(provider.get('name', None), embed_url.netloc):
                    params = {"embed_url": embed_url}
                    params['provider_name'] = embed_dict['site_name'] if 'site_name' in embed_dict else None
                    params['thumbnail_url'] = embed_dict['image'] if 'image' in embed_dict else None
 
                    if provider.get('height', False) and 'height' in embed_dict:
                        params['height'] = embed_dict.get('height', None)
 
                    return GenericEmbed(embed_dict['url'], params)
 
            # This should be a "generic" case, mostly comming from og:video
            # Chose to disable it as it's very difficult to make it work for any generic case
            # Check http://soc.li/SHxUtad
            #return generic_video_dict(url, video_type)
            return None
        return None
 
    @staticmethod
    def get_embed_dict(url, params=None):
        """Return a dict with the video
 
        this method is for to keep the compatibility for old
 
        """
        embed = EmbedFactory.get_embed(url, params)
        return embed.get_embed_dict() if embed else None
 
    @staticmethod
    def is_supported(url):
        if not url:
            return False
 
        p = urlparse.urlparse(url)
        #change it explicit names TODO
        for embed_subclass in Embed.__subclasses__():
            # SlideSharePresentation it's not included, cuz it has its own parser scraper.parsers.slideshare
            if embed_subclass.check_url(parse_url=p):  # and embed_resource_subclass != SlideSharePresentation:
                return True
        return False
 
    @staticmethod
    def _livestream_clean(embed_url):
        '''clean the embed_url value for site like livestream
        livestream send a player url like this
 
        &lt;iframe src=&quot;http://api.new.livestream.com/accounts/57501/events/1146195/videos/4796901.html?width=640&amp;height=360&quot; width=&quot;640&quot; height=&quot;360&quot; frameborder=&quot;0&quot; scrolling=&quot;no&quot;&gt;&lt;/iframe&gt;
        '''
        #TODO improve it, this method shouldnt be here.
        from BeautifulSoup import BeautifulSoup
        embed_decode = BeautifulSoup(embed_url, convertEntities=BeautifulSoup.HTML_ENTITIES)
        if embed_decode.iframe and embed_decode.iframe['src']:
            u = urlparse.urlparse(embed_decode.iframe['src'])
            return '%s://%s%s?width=430&height=310' % (u.scheme, u.netloc, u.path)
        return ''
 
 
class Embed(object):
    """
    Parent class represent an external video.
    """
 
    provider_name = ''
    provider_url = ''
    video_id = ''
    original_url = ''
    thumbnail_url = ''
    embed_url = ''
    height = None
    width = None
 
    def __init__(self, url, params=None):
        self.original_url = url
        self.parms = params
 
    def get_original_url(self):
        """Return original url."""
        return self.original_url
 
    def get_url(self):
        """Return canonical url."""
        raise NotImplementedError("Subclass must implement abstract method get_url")
 
    def get_embed_url(self):
        """Return an url to be embed."""
        raise NotImplementedError("Subclass must implement abstract method get_embed_url")
 
    def get_thumbnail_url(self):
        """Return an url for thumbnail related to videos."""
        raise NotImplementedError("Subclass must implement abstract method get_thumbnail_url")
 
    def get_height(self):
        """Return custom height."""
        return self.height
 
    def get_width(self):
        """Return custom width."""
        return self.width
 
    def get_provider_url(self):
        """Return provider url."""
        return self.provider_url
 
    def get_provider_name(self):
        """Return provider name."""
        return self.provider_name
 
    def _oembed_request(self, url):
        """ This method must be used when any class needs to do an oembed request"""
        try:
            response = cache.get(url)
            if not response:
                resp = urllib.urlopen(url, timeout=5)
                response = json.loads(resp.read())
                cache.set('embed_'.format(url), response, 60 * 60 * 6)  # 6hrs para que se actualize cada tanto
            return response
        except (urllib.URLError, ValueError, IndexError, TimeoutException, BadStatusLine, ssl.SSLError):
            return {}
 
    def get_embed_dict(self):
        """Return a dict with the video."""
        if not self.get_url() or not self.get_embed_url():
            return None
 
        output = {
            "url": self.get_url(),
            "embed_url": self.get_embed_url(),
            "provider_url": self.get_provider_url(),
            "provider_name": self.get_provider_name(),
            "thumbnail_url": self.get_thumbnail_url(),
            "type": "video"
        }
        if self.get_height():
            output['iframe_height'] = self.get_height()
        if self.get_width():
            output['iframe_width'] = self.get_width()

        return output
 
    @staticmethod
    def check_url(url=None, parse_url=None):
        """Check if the url correspond to this class"""
        return False
 
 
class Spotify(Embed):
 
    provider_name = "Spotify"
    provider_url = "http://www.spotify.com/"
 
    def __init__(self, url, params=None):
 
        super(Spotify, self).__init__(url, params)
        self._get_ids()
 
    def _get_ids(self):
 
        p = urlparse.urlparse(self.original_url)
        try:
            split_list = p.path.split('/')
            self._type = split_list[-2:][0]
            self._id = split_list[-1:][0]
            if len(split_list) == 5:
                self._user = split_list[-4:][0]
                self._user_name = split_list[-3:][0]
        except IndexError:
            pass
 
    def get_url(self):
 
        if self.original_url:
            return self.original_url
 
        return ''
 
    def get_embed_url(self):
 
        embed_url = ''
        if not self._id and not self._type:
            return embed_url
 
        if self._type in ['track', 'album']:
            embed_url = 'https://embed.spotify.com/?uri=spotify:%s:%s' % (self._type, self._id)
        elif self._type == 'playlist':
            embed_url = 'https://embed.spotify.com/?uri=spotify:%s:%s:%s:%s' % (self._user, self._user_name, self._type, self._id)
 
        return embed_url
 
    def get_thumbnail_url(self):
 
        return ''
 
    @staticmethod
    def check_url(url=None, parse_url=None):
        if not parse_url:
            parse_url = urlparse.urlparse(url)
        return parse_url.netloc.endswith('spotify.com') and re.search(r'^/\w+/\w+', parse_url.path)


class YoutubeVideo(Embed):
    """
    Implementation to support Youtube videos.
    """
 
    provider_name = "Youtube"
    provider_url = "http://www.youtube.com"
 
    def __init__(self, url, params=None):
        """Constructor
        setting from the start the video_id
 
        """
        super(YoutubeVideo, self).__init__(url, params)
        self.video_id = self.get_video_id()
 
    def get_video_id(self):
        """Returns a youtube video id from a url
 
        Supports urls of type:
        http://www.youtube.com/watch?v=KRaeHxwZvms&feature=g-u-u&context=G2b00124FUAAAAAAAAAA
        http://www.youtube.com/v/KRaeHxwZvms?showsearch=0
        http://www.youtube.com/embed/KRaeHxwZvms?fs=1&feature=oembed
        http://www.youtube-nocookie.com/embed/hFbyujLT8HQ?autohide=1&theme=light&hd=1&modestbranding=1&rel=0&showinfo=0&showsearch=0&wmode=transparent # pinterest
        http://youtu.be/YGa_oEsVkHM
        http://www.youtube.com/user/leweb#p/u/1/Ph33ElIbK64
        http://www.youtube.com/Scobleizer#p/u/1/1p3vcRhsYGo
 
        """
        if self.video_id:
            return self.video_id
 
        if not self.original_url:
            return ''
 
        p = urlparse.urlparse(self.youtube_fix_url(self.original_url))
        if p.path == '/watch':
            # Url of type http://www.youtube.com/watch?v=KRaeHxwZvms&feature=g-u-u&context=G2b00124FUAAAAAAAAAA
            #logger.debug('is a watch')
            params = cgi.parse_qs(p.query)
            if 'v' in params:
                return params['v'][0]
        elif p.fragment.startswith('/watch?v='):
            # sample. http://m.youtube.com/#/watch?v=ZXkW1-HdRC8
            params = cgi.parse_qs(p.fragment)
            if '/watch?v' in params:
                return params['/watch?v'][0]
        elif p.path.startswith('/v/') or p.path.startswith('/embed/'):
            path = p.path.split('/')
            return path[-1]
        elif p.netloc == 'youtu.be':
            return p.path[1:]
        elif re.match('(.{1}/){3}([\w+-_^/]+)', p.fragment):
            parts = p.fragment.split('/')
            return parts[-1]
        return ''
 
    def get_url(self):
        if not self.get_video_id():
            return ''
 
        return 'http://www.youtube.com/watch?v=%s' % self.get_video_id()
 
    def get_embed_url(self):
        """Returns the embed url for a youtube video."""
        if not self.get_video_id():
            return ''
 
        if not self.embed_url:
            self.embed_url = 'https://www.youtube.com/embed/%s?wmode=transparent' % self.get_video_id()
 
        return self.embed_url
 
    def get_thumbnail_url(self):
        """Returns the thumbnail url for a youtube video."""
        if not self.get_video_id():
            return ''
 
        if not self.thumbnail_url:
            self.thumbnail_url = 'https://img.youtube.com/vi/%s/hqdefault.jpg' % self.get_video_id()
 
        return self.thumbnail_url
 
    @staticmethod
    def youtube_fix_url(url):
        """
        Fixes some malformed urls that are around on some sites, which looks like
        http://www.youtube.com/embed/dmKZhZjz6Ks&showsearch=0?fs=1
 
        """
        p = urlparse.urlparse(url)
        path = p.path
        if '&' in p.path:
            # sign of a malformed path
            path = re.sub('\&.+', '', p.path)
        return urlparse.urlunparse((p.scheme, p.netloc, path, p.params, p.query, p.fragment))
 
    @staticmethod
    def is_youtube_user(url=None, parse_url=None):
        """Returns if the url is for users urls.
 
        also if is an valid user url but had the fragment #p/1/u/video_id return False.
        because represent a video.
 
        """
 
        if not parse_url:
            if url:
                parse_url = urlparse.urlparse(url)
            else:
                return False
 
        if re.match('(.{1}/){3}([\w+-_^/]+)', parse_url.fragment):
            return False
 
        return parse_url.path.startswith('/user/')
 
    @staticmethod
    def check_url(url=None, parse_url=None):
        """Returns True if the url is an url with youtube videos
 
        Domains supported:
        'youtube.com', 'youtube-nocookie.com', 'youtu.be', 'youtube.googleapis.com'
 
        """
 
        if not parse_url:
            if url:
                parse_url = urlparse.urlparse(url)
 
        #yt_domains = ['youtube.com', 'youtube-nocookie.com', 'youtu.be', 'youtube.googleapis.com']
        #return any(parse_url.netloc.endswith(yt) for yt in yt_domains)
        return re.search('^(.+\.)*(youtube(-nocookie|\.googleapis)?.com|youtu.be)+$', parse_url.netloc)
 
 
class VimeoVideo(Embed):
    """
    Implementation to support Youtube videos.
    """
 
    provider_name = "vimeo"
    provider_url = "http://www.vimeo.com/"
 
    def __init__(self, url, params=None):
        """Constructor
        setting from the start the video_id
 
        """
        super(VimeoVideo, self).__init__(url, params)
        self.video_id = self.get_video_id()
        self.thumbnail_url = ''
 
    def get_video_id(self):
        """Returns a vimeo video id from a url
        Supports urls of type:
 
        http://vimeo.com/21347521
        http://player.vimeo.com/video/21347521?title=0&amp;byline=0&amp;portrait=0
        http://vimeo.com/moogaloop.swf?clip_id=21347521&amp;server=vimeo.com&amp;show_title=0&amp;show_byline=0&amp;show_portrait=0&amp;color=00adef&amp;fullscreen=1&amp;autoplay=0&amp;loop=0" # OLD embed code
        NOT http://player.vimeo.com/hubnut/album/2458827?color=44bbff&background=000000&slideshow=1&video_title=1&video_byline=0
        """
        if self.video_id:
            return self.video_id
 
        if not self.original_url:
            return ''
 
        p = urlparse.urlparse(self.original_url)
        if p.netloc.endswith('vimeo.com') and 'hubnut/album/' in p.path:
            return ''
 
        if p.netloc.endswith('vimeo.com') and p.path.split('/')[-1:][0].isdigit():
            # Url of type http://vimeo.com/21347521
            # mobile type http://vimeo.com/m/21347521
            return p.path.split('/')[-1:][0]
        elif p.netloc.endswith('vimeo.com') and p.path == '/moogaloop.swf' and 'clip_id' in p.query:
            # Old embed code style url
            #params = dict([part.split('=') for part in p.query.split('&')])
            params = cgi.parse_qs(p.query)
            if 'clip_id' in params:
                return params['clip_id'][0]
        elif p.netloc == 'player.vimeo.com' and p.path.startswith('/video/'):
            # Url of type http://player.vimeo.com/video/21347521?title=0&amp;byline=0&amp;portrait=0
            path = p.path.split('/')
            return path[-1]
 
        return ''
 
    def get_url(self):
        """Returns a vimeo "canonical" url."""
        if not self.get_video_id():
            return ''
 
        return 'http://www.vimeo.com/%s' % self.get_video_id()
 
    def get_embed_url(self):
        """Returns the embed url for a vimeo video."""
        if not self.get_video_id():
            return ''
 
        return 'https://player.vimeo.com/video/%s' % self.get_video_id()
 
    def get_thumbnail_url(self):
        """
        Get vimeo thumbnail from vimeo's json api (one more network request but worth the effort)
        """
 
        if self.thumbnail_url:
            return self.thumbnail_url
 
        if not self.get_video_id():
            return ''
 
        api_url = 'http://vimeo.com/api/v2/video/%s.json' % self.get_video_id()
        try:
            res = self._oembed_request(api_url)[0]
        except KeyError:
            return ''
        self.thumbnail_url = res.get('thumbnail_large', '')
        return self.thumbnail_url
 
    @staticmethod
    def check_url(url=None, parse_url=None):
        """Returns True if the url is an url with vimeo videos
 
        Domains supported:
        vimeo.com
 
        """
 
        if not parse_url:
            parse_url = urlparse.urlparse(url)
 
        return (parse_url.netloc == 'vimeo.com' or parse_url.netloc.endswith('.vimeo.com')) and 'hubnut/album/' not in parse_url.path
 
 
class LivestreamVideo(Embed):
    """
    Implementation to support Livestream.
    the old livestream.
    Tue Oct  2 16:30:44 UTC 2012
    """
 
    provider_name = "Livestream"
    provider_url = "http://www.livestream.com/"
    livestream_user = None
 
    def __init__(self, url, params=None):
        """Constructor
        setting from the start the video_id
 
        """
        super(LivestreamVideo, self).__init__(url, params)
        self.video_id = self.get_video_id()
        self.livestream_user = self.get_username()
 
    def get_video_id(self):
        """Returns a livestream video id from a url
 
        Supports urls of type:
        http://www.livestream.com/xprize
        http://www.livestream.com/xprize/video?clipId=pla_1a25a2ba-9ca4-4c3b-b1b1-ebd7d79ef6d2&utm_source=lslibrary&utm_medium=ui-thumb
        http://cdn.livestream.com/embed/xprize?layout=4&amp;clip=pla_1a25a2ba-9ca4-4c3b-b1b1-ebd7d79ef6d2&amp;width=560&amp;autoplay=false
        http://new.livestream.com/Fox8News/live/videos/4796901
        http://livestre.am/utDh
        http://cdn.livestream.com/hdembed/index.html?account_id=57501&event_id=1146195
        http://new.livestream.com/nytimes/GiadaDeLaurentiis-BobbyFlay
        """
 
        if self.video_id:
            return self.video_id
 
        if not self.original_url:
            return ''
 
        p = urlparse.urlparse(self.original_url)
        params = cgi.parse_qs(p.query)
 
        if p.path.endswith('/video'):
            # url type http://www.livestream.com/xprize/video?clipId=pla_1a25a2ba-9ca4-4c3b-b1b1-ebd7d79ef6d2
            if 'clipId' in params:
                return params['clipId'][0]
        if p.path.startswith('/embed'):
            # url type http://cdn.livestream.com/embed/xprize?layout=4&amp;clip=pla_1a25a2ba-9ca4-4c3b-b1b1-ebd7d79ef6d2&amp;width=560&amp;autoplay=false
            if 'clip' in params:
                return params['clip'][0]
 
        return ''
 
    def get_username(self):
        """Returns a livestream username from a url
 
        Supports urls of type:
        http://www.livestream.com/xprize
        http://www.livestream.com/xprize/video?clipId=pla_1a25a2ba-9ca4-4c3b-b1b1-ebd7d79ef6d2&utm_source=lslibrary&utm_medium=ui-thumb
        http://cdn.livestream.com/embed/xprize?layout=4&amp;clip=pla_1a25a2ba-9ca4-4c3b-b1b1-ebd7d79ef6d2&amp;width=560&amp;autoplay=false
        http://new.livestream.com/Fox8News/live/videos/4796901
        """
 
        if self.livestream_user:
            return self.livestream_user
 
        if not self.original_url:
            return ''
 
        p = urlparse.urlparse(self.original_url)
        path_term = p.path.split('/')
 
        if len(path_term) == 3:
            if path_term[2] == 'video':
                # url type http://www.livestream.com/xprize/video?clipId=pla_1a25a2ba-9ca4-4c3b-b1b1-ebd7d79ef6d2
                return path_term[1]
            if path_term[1] == 'embed':
                # url type http://cdn.livestream.com/embed/xprize?layout=4&amp;clip=pla_1a25a2ba-9ca4-4c3b-b1b1-ebd7d79ef6d2&amp;width=560&amp;autoplay=false
                return path_term[2]
 
        return ''
 
    def get_url(self):
        """Returns a livestream "canonical" url."""
        if not self.get_video_id() or not self.get_username():
            return ''
 
        return 'http://www.livestream.com/%s/video?clipId=%s' % (self.get_username(), self.get_video_id())
 
    def get_embed_url(self):
        """
        Returns the embed url for a livestream video
        """
        if not self.get_video_id() or not self.get_username():
            return ''
 
        return 'http://cdn.livestream.com/embed/%s?layout=4&amp;clip=%s' % (self.get_username(), self.get_video_id())
 
    def get_thumbnail_url(self):
        """
        Query livestream json api to get thumbnail url
        """
        if self.thumbnail_url:
            return self.thumbnail_url
 
        if not self.get_video_id() or not self.get_username():
            return ''
 
        channel_formated = 'x%sx' % (self.get_username().replace('_', '-'))
        api_url = 'http://%s.api.channel.livestream.com/2.0/thumbnail.json?id=%s' % (channel_formated, self.get_video_id())
 
        res = self._oembed_request(api_url)
        thumbnail = res.get('thumbnail', {})
        self.thumbnail_url = thumbnail.get('@url', '')
        return self.thumbnail_url
 
    @staticmethod
    def check_url(url=None, parse_url=None):
        """Returns True if the url is an url with livestream videos
 
        Domains supported:
        livestream.com
 
        """
        if not parse_url:
            parse_url = urlparse.urlparse(url)
 
        unsupported = ['twitcam.', 'new.']
        return parse_url.netloc.endswith('livestream.com')\
            and not any(x in parse_url.netloc for x in unsupported)\
            and len(parse_url.path.split('/')) > 2
 
 
#       #TWITCAM DISABLED, for IE<=9 don't load well.
#class TwitcamVideo(Embed):
#   """
#   Implementation to support TwitcamVideo.
#   Wed Oct 24 08:57:08 UTC 2012
#   """
#
#   provider_name = "Twitcam"
#   provider_url = "http://twitcam.livestream.com/"
#
#   def __init__(self, url, params=None):
#       """Constructor
#       setting from the start the video_id
#
#       """
#       super(TwitcamVideo, self).__init__(url, params)
#       self.video_id = self.get_video_id()
#
#   def get_video_id(self):
#       """Returns a livestream video id from a url
#
#       Supports urls of type:
#       http://twitcam.livestream.com/ajt62
#       http://twitcam.livestream.com/ci7w9
#       """
#       if self.video_id:
#           return self.video_id
#
#       if not self.original_url:
#           return None
#
#       p = urlparse.urlparse(self.original_url)
#       path_term = p.path.split('/')
#
#       if len(path_term) == 2:
#           return path_term[1]
#
#       return None
#       """
#
#   def get_url(self):
#       """Returns a livestream "canonical" url."""
#       if not self.get_video_id():
#           return ''
#
#       return 'http://twitcam.livestream.com/%s' % self.get_video_id()
#
#   def get_embed_url(self):
#       """
#       Returns the embed url for a twitcam.livestream video
#       """
#       if not self.get_video_id():
#           return ''
#
#       url = 'https://static.livestream.com/grid/LSPlayer.swf?hash=%s' % self.get_video_id()
#       return '%s/res/scraper/embed?url=%s' % (settings.BASE_URL, quote(url.encode("utf-8"), ''))
#
#   def get_thumbnail_url(self):
#       """
#       Query livestream json api to get thumbnail url
#       """
#       return ''
#
#   @staticmethod
#   def check_url(url=None, parse_url=None):
#       """Returns True if the url is an url with twitcam videos
#
#       Domains supported:
#       twitter.livestream.com
#
#        """
#        if not parse_url:
#            parse_url = urlparse.urlparse(url)
#
#        return parse_url.netloc.endswith('twitcam.livestream.com')
 
 
class DailymotionVideo(Embed):
    """
    Implementation to support Youtube videos.
    """
 
    provider_name = "Dailymotion"
    provider_url = "http://www.dailymotion.com/"
 
    def __init__(self, url, params=None):
        """Constructor
        setting from the start the video_id
 
        """
        super(DailymotionVideo, self).__init__(url, params)
        self.video_id = self.get_video_id()
 
    def get_video_id(self):
        """Returns a dailymotion video id from a url
 
        Supports urls of type:
        http://www.dailymotion.com/embed/video/xmp7zw
        http://www.dailymotion.com/video/xmp7zw_whatever
        http://www.dailymotion.com/swf/video/xmp7zw_whatever
        http://www.dailymotion.com/swf/xmp7zw
 
        """
 
        if self.video_id:
            return self.video_id
 
        if not self.original_url:
            return ''
 
        #logger.debug('DAILYMOTION VIDEO FOUND %s' % url)
 
        p = urlparse.urlparse(self.original_url)
        path = p.path
        if path.endswith('/'):
            path = path[:-1]
        path_list = path[1:].split('/')
 
        if len(path_list) == 3 and (p.path.startswith('/embed/video/') or p.path.startswith('/swf/video/')):
            # http://www.dailymotion.com/embed/video/xmp7zw
            return re.sub('_.+', '', path_list[2])
        elif len(path_list) == 2 and (p.path.startswith('/video/') or p.path.startswith('/swf/')):
            # http://www.dailymotion.com/video/xmp7zw_whatever
            # http://www.dailymotion.com/swf/xmp7zw
            return re.sub('_.+', '', path_list[1])
 
        return ''
 
    def get_url(self):
        """Returns a dailymotion "canonical" url."""
        if not self.get_video_id():
            return ''
 
        return 'http://www.dailymotion.com/%s' % self.get_video_id()
 
    def get_embed_url(self):
        """
        Returns the embed url for a dailymotion video
        """
        if not self.get_video_id():
            return ''
 
        return 'https://www.dailymotion.com/embed/video/%s' % self.get_video_id()
 
    def get_thumbnail_url(self):
        """
        Query dailymotion json api to get thumbnail url
        https://api.dailymotion.com/video/x7lni3?fields=thumbnail_url
        """
        if self.thumbnail_url:
            return self.thumbnail_url
 
        if not self.get_video_id():
            return ''
 
        if not self.thumbnail_url:
            api_url = 'https://api.dailymotion.com/video/%s?fields=thumbnail_url' % self.get_video_id()
        res = self._oembed_request(api_url)
        self.thumbnail_url = res.get('thumbnail_url', '')
        return self.thumbnail_url
 
    @staticmethod
    def check_url(url=None, parse_url=None):
        """Returns True if the url is an url with dailymotion videos
 
        Domains supported:
        dailymotion.com
 
        """
 
        if not parse_url:
            parse_url = urlparse.urlparse(url)
 
        return parse_url.netloc == 'dailymotion.com' or parse_url.netloc.endswith('.dailymotion.com')
 
 
class GenericEmbed(Embed):
    """
    Implementation to support generic video.
    Wed Oct  3 21:56:11 UTC 2012
    author:flavin
 
    provider tested:
    - new.livestream.com
        http://new.livestream.com/Fox8News/live/videos/4796901
    - tout.com
        http://www.tout.com/m/sedgb4
    - abcnews.com, but don't have parameter to autoplay false
        http://abcnews.go.com/US/video/chase-suspect-shoots-himself-on-live-tv-17351163
    - msnbc
        http://video.msnbc.msn.com/nbcnews.com/49259003/?__utma=238145375.1904630803.1347654033.1349302734.1349343323.3&__utmb=238145375.7.9.1349343401839&__utmc=238145375&__utmx=-&__utmz=238145375.1349302734.2.2.utmcsr=nbcnews.com|utmccn=(referral)|utmcmd=referral|utmcct=/&__utmv=238145375.|8=Earned%20By=msnbc%7Cvideo=1^12=Landing%20Content=Mixed=1^13=Landing%20Hostname=www.msnbc.msn.com=1^30=Visit%20Type%20to%20Content=Earned%20to%20Mixed=1&__utmk=56831593#49237464
    - cbsnews
        http://www.cbsnews.com/video/watch/?id=7424242n&tag=flyOutNavigation;flyoutlead3
    - kickstarter
       http://www.kickstarter.com/projects/1245719024/orezom-trails?ref=home_spotlight
    - myspace
        http://www.myspace.com/video/trojancharged/b-o-b-on-the-b-side-episode-2/108943535
    - 5min
        http://www.5min.com/Video/Balmain-Spring-2013-Ready-To-Wear-at-Paris-Fashion-Week-517493874
    - wordpress tv
        http://wordpress.tv/2012/10/03/scott-offord-seo-for-wordpress-how-to-avoid-penalties-from-google-and-bing/
 
    """
 
    def __init__(self, url, params={}):
        """Constructor
        get in params parameter the values to fill up the video.
 
        """
        super(GenericEmbed, self).__init__(url, params)
 
        u = urlparse.urlparse(url)
 
        if params.get('provider_name'):
            self.provider_name = params['provider_name']
        else:
            self.provider_name = u.netloc
 
        if params.get('provider_url'):
            self.provider_url = params['provider_url']
        else:
            self.provider_url = u.scheme + '://' + u.netloc
 
        if params.get('thumbnail_url'):
            self.thumbnail_url = params['thumbnail_url']
 
        if params.get('height'):
            self.height = params['height']
 
        if params.get('width'):
            self.width = params['width']
 
        if 'embed_url' in params:
            self.embed_url = self._prepare_embed_url(params['embed_url'])
 
    def get_url(self):
        """Return canonical url."""
        return self.original_url
 
    def get_embed_url(self):
        """Return an url to be embed."""
        return self.embed_url
 
    def get_thumbnail_url(self):
        """Return an url for thumbnail related to videos."""
        return self.thumbnail_url
 
    def _prepare_embed_url(self, url):
        """Return embed url"""
 
        u = url if type(url) == urlparse.ParseResult else urlparse.urlparse(url)
        q = cgi.parse_qs(unquote(u.query.encode("utf-8")))
 
        #remove autoplay if you know more add here
        for x in ('autoplay', 'autoPlay', 'autostart'):
            if x in q:
                del q[x]
        # not work
        # if 'wmode' not in q:
        #    q['wmode'] = 'opaque'
 
        if '.swf' in u.path and u.scheme == 'https':
            url = urlparse.urlunparse((u.scheme, u.netloc, u.path, u.params, urlencode(q, True), u.fragment))
            embed_url = '%s/res/scraper/embed?url=%s' % (settings.BASE_URL, quote(url.encode("utf-8"), ''))
        else:
            embed_url = urlparse.urlunparse((u.scheme, u.netloc, u.path, u.params, urlencode(q, True), u.fragment))
 
        return embed_url
 
 
class SlideSharePresentation(Embed):
    """
    Implementation to support SlideShare Presentation.
    """
 
    provider_name = "Slide Share"
    provider_url = "http://www.slideshare.net/"
 
    def __init__(self, url, params=None):
        """Constructor
        setting from the start the video_id
 
        """
        super(SlideSharePresentation, self).__init__(url, params)
        api_url = 'http://www.slideshare.net/api/oembed/2?url=%s&format=json' % (url)
        self.res = self._oembed_request(api_url)
        self.video_id = self.get_video_id()
        self.thumbnail_url = ''
 
    def get_video_id(self):
        """Returns a dailymotion video id from a url
 
        Supports urls of type:
        http://www.slideshare.net/slideshow/embed_code/1293644
 
        """
 
        if self.video_id:
            return self.video_id
 
        if not self.original_url:
            return ''
 
        if self.res.get('slideshow_id'):
            return self.res.get('slideshow_id')
 
        p = urlparse.urlparse(self.original_url)
        path = p.path
        if path.endswith('/'):
            path = path[:-1]
        path_list = path[1:].split('/')
 
        if len(path_list) == 3 and (p.path.startswith('/slideshow/embed_code')):
            # http://www.slideshare.net/slideshow/embed_code/1293644
            return path_list[2]
        elif len(path_list) == 2 and p.path.startswith('/swf'):
            # return -1 when url is like : http://static.slideshare.net/swf/ssplayer2.swf?doc=working-dogs-1201800078341935-2
            # FixMe :slideshare oembed api doesnt support this kind of url
            return -1
        return ''
 
    def get_url(self):
        """Returns a dailymotion "canonical" url."""
        if not self.get_video_id():
            return ''
 
        if self.get_video_id() == -1:
            return self.original_url
 
        return 'http://www.slideshare.net/slideshow/embed_code/%s' % self.get_video_id()
 
    def get_embed_url(self):
        """
        Returns the embed url for a dailymotion video
        """
        if not self.get_video_id():
            return ''
 
        if self.get_video_id() == -1:
            return self.original_url
 
        return 'https://www.slideshare.net/slideshow/embed_code/%s' % self.get_video_id()
 
    def get_thumbnail_url(self):
        """
        Query SlideShare  json api to get thumbnail url
        """
        if self.thumbnail_url:
            return self.thumbnail_url
 
        if not self.get_video_id():
            return ''
 
        if self.get_video_id() == -1:
            return ''
 
        if not self.thumbnail_url:
            thumb_url = self.res.get('slide_image_baseurl', '')
            thumb_suffix = self.res.get('slide_image_baseurl_suffix', '')
            if thumb_url and thumb_suffix:
                #hardcode: "1" means the slide that we want to show as thumbnail.
                # this case is slide number 1 of presentation.
                thumb_url = ''.join(['https:', thumb_url, '1', thumb_suffix])
                self.thumbnail_url = thumb_url
 
        return self.thumbnail_url
 
    @staticmethod
    def check_url(url=None, parse_url=None):
        """Returns True if the url is an url with youtube videos
 
        Domains supported:
        slideshare.net
 
        """
 
        if not parse_url:
            parse_url = urlparse.urlparse(url)
 
        return parse_url.netloc.endswith('slideshare.net')
 
 
class SoundcloudEmbed(Embed):
    """
    Implementation to support embeds of soundcloud
    Sun Dec 16 05:34:35 UTC 2012
    """
 
    provider_name = "Soundcloud"
    provider_url = "http://www.soundcloud.com/"
 
    def __init__(self, url, params=None):
        """Constructor"""
        #removing #fragment and ?query from url
 
        super(SoundcloudEmbed, self).__init__(url, params)
        self._oembed = self._get_oembed(url)
 
        u = urlparse.urlparse(url)
        self.original_url = urlparse.urlunsplit((u.scheme, u.netloc, u.path, '', ''))
 
    def get_url(self):
        """Returns the url."""
        return self.original_url
 
    def get_embed_url(self):
        """Returns the embed url for a soundcloud embed."""
        if not self._oembed:
            return ''
 
        if not self.original_url:
            return ''
 
        return 'https://w.soundcloud.com/player/?url=%s' % (self.original_url)
 
    def get_thumbnail_url(self):
        """Query json api to get thumbnail url."""
        if not self._oembed:
            return ''
 
        if not self.thumbnail_url:
            self.thumbnail_url = self._oembed.get('thumbnail_url', '')
 
        return self.thumbnail_url
 
    def get_height(self):
        """Query json api to get height."""
        if self.height:
            return self.height
 
        if not self._oembed:
            return ''
 
        return self._oembed.get('height', None)
 
    def _get_oembed(self, url):
        """Return json of soundcloud embed"""
        api_url = 'http://www.soundcloud.com/oembed/?url=%s&format=json' % (url)
        return self._oembed_request(api_url)
 
    @staticmethod
    def check_url(url=None, parse_url=None):
        """Returns True if is a possible link with embed"""
 
        if not parse_url:
            parse_url = urlparse.urlparse(url)
 
        invalid_paths = ['^\/?$', '^\/(stream|explore|groups|upload|you|dashboard|messages|settings|creativecommons|tracks|people)(\/|$)']
 
        return parse_url.netloc in ['soundcloud.com', 'www.soundcloud.com', 'm.soundcloud.com']\
            and not any(re.search(invalid_path, parse_url.path) for invalid_path in invalid_paths)
 
 
class BambuserEmbed(Embed):
    """
    Implementation to support embeds of bambuser
    Sun Dec 16 15:20:04 UTC 2012
    """
 
    provider_name = "Bambuser"
    provider_url = "http://www.bambuser.com/"
 
    def __init__(self, url, params=None):
        """Constructor"""
        super(BambuserEmbed, self).__init__(url, params)
        self.video_id = self.get_video_id()
 
    def get_video_id(self):
        """Returns a video id
 
        Supports urls of type:
        http://bambuser.com/v/3152023
        http://embed.bambuser.com/broadcast/2993563
        http://bambuser.com/v/3121631.live
        """
 
        if self.video_id:
            return self.video_id
 
        if not self.original_url:
            return ''
 
        p = urlparse.urlparse(self.original_url)
 
        if p.path.startswith('/v/') or p.path.startswith('/broadcast/'):
            path = p.path.split('/')
            if len(path) == 3:
                return p.path.split('/')[-1].replace('.live', '')
 
        return ''
 
    def get_url(self):
        """Returns the url."""
        return self.original_url
 
    def get_embed_url(self):
        """Returns the embed url."""
        if not self.original_url:
            return ''
 
        if not self.video_id:
            return ''
 
        return 'http://embed.bambuser.com/broadcast/%s?context=b_simple&autoplay=0&chat=0' % (self.video_id)
 
    def get_thumbnail_url(self):
        """Return thumbnail"""
        return ''
 
    @staticmethod
    def check_url(url=None, parse_url=None):
        """Returns True if is a possible link with embed"""
 
        if not parse_url:
            parse_url = urlparse.urlparse(url)
 
        return parse_url.netloc.endswith('bambuser.com')\
            and bool(re.search('^\/(v|broadcast)\/\d+(\.live)?$', parse_url.path))
 
 
class VineEmbed(Embed):
    """
    Supports new embed vine code (as of Apr 15th, 2013)
    """
 
    provider_name = "Vine"
    provider_url = "http://vine.co/"
 
    def __init__(self, url, params=None):
        """Constructor"""
        super(VineEmbed, self).__init__(url, params)
        self.video_id = self.get_video_id()
        self.height = 'width'
        self.thumbnail_url = ''
 
    def get_video_id(self):
        """Returns a vine video id from a url
        Supports urls of type:
 
        https://vine.co/v/bjHh0zHdgZT
        """
        if self.video_id:
            return self.video_id
 
        if not self.original_url:
            return ''
 
        p = urlparse.urlparse(self.original_url)
        path = p.path
        if path.endswith('/'):
            path = path[:-1]
        path_list = path[1:].split('/')
 
        if path_list[0] == 'v':
            # https://vine.co/v/bjHh0zHdgZT
            return path_list[1]
 
        return ''
 
    def get_url(self):
        """Returns the url."""
        if not self.original_url or not self.get_video_id():
            return ''
 
        return 'https://vine.co/v/%s' % (self.get_video_id())
 
    def get_embed_url(self):
        """Returns the embed url for a vine embed."""
        if not self.original_url:
            return ''
 
        return 'https://vine.co/v/%s/embed/simple' % (self.get_video_id())
 
    def get_height(self):
        """Vine videos are square"""
        return 'width'
 
    def get_thumbnail_url(self):
        """
        Gets vine video thumbnail by checking the very same url of the vine video
        """
        if self.thumbnail_url:
            return self.thumbnail_url
 
        if not self.get_video_id():
            return ''
 
        vine_url = self.get_url()
        res = self._http_request(vine_url)
        m = re.search(r'property="og:image" content="(?P<thumbnail>[^"]*)"', res)
        if m and m.groupdict():
            self.thumbnail_url = m.groupdict().get('thumbnail') or ''
 
        return self.thumbnail_url
 
    @staticmethod
    def check_url(url=None, parse_url=None):
        """Returns True if the url is an url with vine videos
 
        Domains supported:
        vine.co
 
        """
        if not parse_url:
            parse_url = urlparse.urlparse(url)
 
        return (parse_url.netloc == 'vine.co' or parse_url.netloc.endswith('.vine.co')) \
            and re.search('/v/\w', parse_url.path) is not None
 
    def _http_request(self, url):
        """Make an http request to vine.co"""
        try:
            opener = urllib.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            response = opener.open(url, None)
            #response = urllib.urlopen(url, timeout=5)
            return response.read()
        except (urllib.URLError, ValueError, IndexError, TimeoutException, BadStatusLine):
            return ''


class Vzaar(Embed):
    provider_name = 'Vzaar'
    provider_url = 'http://vzaar.com/'
    xml_response = None
    video_error = None
    id_video = None

    def __init__(self, url, params=None):
        super(Vzaar, self).__init__(url, params=params)
        self.set_init_id()
        self.consult_api()

    def set_init_id(self):
        url_parse = urlparse.urlparse(self.original_url)
        if url_parse.netloc == 'vzaar.com':
            self.id_video = url_parse.path.split('videos/')[1].strip().replace("/","")
        elif url_parse.netloc == 'vzaar.tv':
            self.id_video = url_parse.path.strip().replace("/","")

    def consult_api(self):
        response = None
        if self.id_video:
            try:
                response = requests.get('http://vzaar.com/api/videos/{0}.xml'.format(self.id_video), timeout=5)
                response.raise_for_status()
            except requests.exceptions.RequestException, e:
                self.error_message = e

            if response is not None:
                self.xml_response = ET.fromstring(response.text.encode('utf-8'))
                xml = response.text.encode('utf-8')

                if self.xml_response.find('video_status_id') is None:
                    self.video_error = "Video no disponible"
                    self.xml_response = None
                else:
                    if self.xml_response.find('video_status_id').text != '2':
                        self.xml_response = self.xml_response.find('video_status_id')

    def get_video_id(self):
        if not self.id_video or not self.original_url or not self.xml_response:
            return ''
        return self.id_video

    def get_url(self):
        """Return canonical url."""
        if not self.id_video or not self.original_url or not self.xml_response:
            return '' if not self.video_error else self.video_error

        return self.xml_response.find('video_url').text
 
    def get_embed_url(self):
        """Return an url to be embed."""
        if not self.id_video or not self.original_url or not self.xml_response:
            return ''
        return '//view.vzaar.com/{0}/player'.format(self.id_video)
 
    def get_thumbnail_url(self):
        """Return an url for thumbnail related to videos."""
        if not self.id_video or not self.original_url or not self.xml_response:
            return ''
        return self.xml_response.find('framegrab_url').text

    def get_html(self):
        """Return an url for thumbnail related to videos."""
        if not self.id_video or not self.original_url or not self.xml_response:
            return ''
        return self.xml_response.find('html').text

    def get_height(self):
        if not self.id_video or not self.original_url or not self.xml_response:
            return ''
        return self.xml_response.find('height').text

    def get_width(self):
        if not self.id_video or not self.original_url or not self.xml_response:
            return ''
        return self.xml_response.find('width').text

    @staticmethod
    def check_url(url=None, parse_url=None):
        """Returns True if the url is an url with vine videos
 
        Domains supported:
        vine.co
 
        """
        if not parse_url:
            parse_url = urlparse.urlparse(url)
 
        return ('vzaar.com' in parse_url.netloc or 'vzaar.tv' in parse_url.netloc)
