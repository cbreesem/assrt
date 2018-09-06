# -*- coding: utf-8 -*-

import re
import os
import sys
import xbmc
import urllib
import requests
import zipfile
import platform
import shutil
import xbmcvfs
import xbmcaddon
import xbmcgui,xbmcplugin
from bs4 import BeautifulSoup

__addon__ = xbmcaddon.Addon()
__author__     = __addon__.getAddonInfo('author')
__scriptid__   = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__version__    = __addon__.getAddonInfo('version')
__language__   = __addon__.getLocalizedString

__cwd__        = xbmc.translatePath( __addon__.getAddonInfo('path') ).decode("utf-8")
__profile__    = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode("utf-8")
__resource__   = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) ).decode("utf-8")
__temp__       = xbmc.translatePath( os.path.join( __profile__, 'temp') ).decode("utf-8")

sys.path.append (__resource__)

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Accept-Encoding': 'gzip, deflate, sdch, br',
           'Accept-Language': 'zh-CN,zh;q=0.8',
           'Connection': 'keep-alive',
           'Upgrade-Insecure-Requests': '1',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}

assrt_API = 'http://assrt.net/sub/?searchword=%s'
assrt_BASE = 'http://assrt.net/'
exts = [".srt", ".sub", ".smi", ".ssa", ".ass" ]

def log(module, msg):
    xbmc.log((u"%s::%s - %s" % (__scriptname__,module,msg,)).encode('utf-8'),level=xbmc.LOGDEBUG )

def normalizeString(str):
    return str

def getFileList(path):
    fileslist = []
    for d in os.listdir(path):
        if os.path.isdir(path+d):
            fileslist.extend(getFileList(path+d+'/'))
        if os.path.isfile(path+d):
            fileslist.append(path+d)
    return fileslist

def extractCompress(file):
    path  = __temp__ + '/subtitles/'
    if os.path.isdir(path): shutil.rmtree(path)
    if not os.path.isdir(path): os.mkdir(path)

    if platform.system() == 'Windows':
        rarPath = 'C:\Program Files\WinRAR'
        sysPath = os.getenv('Path')
        if 'winrar' not in sysPath.lower(): os.environ["Path"] = sysPath+';'+rarPath
        command = "winrar x -ibck %s %s" % (file, path)
    if platform.system() == 'Linux':
        command = 'unrar x %s %s' % (file, path)
    res = os.system(command)
    if res == 0: return getFileList(path)

def getUriLinks(url, page=1):
    lists = []
    try:
        res = requests.get(url+'&page=%d' % page, headers=headers)
    except: return
    else:
        soup = BeautifulSoup(res.content,'html.parser')
        divs = soup.find_all('div',class_='subitem')
        for i in divs:
            title = i.find('a',class_='introtitle')
            if title is None: continue
            name = title.getText().strip().split('/')[-1]
            link = title.get('href')
            content = i.find('div',id='sublist_div').find_all('span')
            for x in content:
                string = x.getText().encode("UTF-8")
                if '语言' in string:
                    if '简' in string or '繁' in string or '双语' in string:
                        lang = '简'
                        language_name = 'Chinese'
                        language_flag = 'zh'
                    elif '英' in string:
                        lang = '英'
                        language_name = 'English'
                        language_flag = 'en'
                    else:
                        lang = '未知'
                        language_name = 'Chinese'
                        language_flag = 'zh'
                else:
                    lang = '未知'
                    language_name = 'Chinese'
                    language_flag = 'zh'
            lists.append({"language_name":language_name, "filename":name, "link":link, "language_flag":language_flag, "rating":"0", "lang":lang})

        number = soup.find('div',class_='pagelinkcard')
        if number is not None and page == 1:
            number = number.find_all('a')
            for i in number:
                if not re.match('\d+',i.getText()) or i.getText() == '1' or '/' in i.getText(): continue
                lists.extend(getUriLinks(url, int(i.getText())))
    return lists

def Search(item):

    log(__name__ ,"Search for [%s] by name" % os.path.basename(item['file_original_path']))
    url = assrt_API % (item['mansearchstr']) if item['mansearch'] else assrt_API % (item['title'])
    links = getUriLinks(url)
    if links:
        for it in links:
            listitem = xbmcgui.ListItem(label=it["language_name"],
                                  label2=it["filename"],
                                  iconImage=it["rating"],
                                  thumbnailImage=it["language_flag"]
                                  )
            listitem.setProperty( "sync", "false" )
            listitem.setProperty( "hearing_imp", "false" )
            url = "plugin://%s/?action=download&link=%s&lang=%s" % (__scriptid__,
                                                                        it["link"],
                                                                        it["lang"].decode('utf8')
                                                                        )
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=False)

def Download(url,lang):
    try: shutil.rmtree(__temp__)
    except: pass
    try: os.makedirs(__temp__)
    except: pass

    lists = []
    try:
        res = requests.get(assrt_BASE+url,headers=headers)
        soup = BeautifulSoup(res.content,'html.parser')
        href = soup.find('div',class_='download').a.get('href')

        headers['Referer'] = assrt_BASE+url
        res = requests.get(assrt_BASE+href,headers=headers)
    except:
        return []
    else:
        fileName = res.headers['Content-Disposition'].replace('"','').split('=')[1]

        tempfile = os.path.join(__temp__, "subtitles.%s" % fileName.split('.')[-1])
        xbmc.log(tempfile)
        with open(tempfile, 'wb') as f:
            f.write(res.content)
            f.close()
        xbmc.sleep(100)
        if tempfile.split('.')[-1].lower() in ('zip','rar'):
            lists = extractCompress(tempfile)
        else:
            lists = [tempfile]

        lists = [i for i in lists if os.path.splitext(i)[1] in exts]

    if len(lists) == 0: return []

    if len(lists) == 1:
        return lists[0]
    else:
        index = [i.split('/')[-1] for i in lists]
        sel = xbmcgui.Dialog().select('请选择压缩包中的字幕', index)
        if sel == -1: sel = 0
        return lists[sel]

def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=paramstring
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]

    return param

params = get_params()
if params['action'] == 'search' or params['action'] == 'manualsearch':
    item = {}
    item['temp']               = False
    item['rar']                = False
    item['mansearch']          = False
    item['year']               = xbmc.getInfoLabel("VideoPlayer.Year")                           # Year
    item['season']             = str(xbmc.getInfoLabel("VideoPlayer.Season"))                    # Season
    item['episode']            = str(xbmc.getInfoLabel("VideoPlayer.Episode"))                   # Episode
    item['tvshow']             = normalizeString(xbmc.getInfoLabel("VideoPlayer.TVshowtitle"))   # Show
    item['title']              = normalizeString(xbmc.getInfoLabel("VideoPlayer.OriginalTitle")) # try to get original title
    item['file_original_path'] = urllib.unquote(xbmc.Player().getPlayingFile().decode('utf-8'))  # Full path of a playing file
    item['3let_language']      = []

    if 'searchstring' in params:
        item['mansearch'] = True
        item['mansearchstr'] = params['searchstring']

    for lang in urllib.unquote(params['languages']).decode('utf-8').split(","):
        item['3let_language'].append(xbmc.convertLanguage(lang,xbmc.ISO_639_2))

    if item['title'] == "":
        item['title']  = xbmc.getInfoLabel("VideoPlayer.Title")                       # no original title, get just Title
        if item['title'] == os.path.basename(xbmc.Player().getPlayingFile()):         # get movie title and year if is filename
            title, year = xbmc.getCleanMovieTitle(item['title'])
            item['title'] = normalizeString(title.replace('[','').replace(']',''))
            item['year'] = year

    if item['episode'].lower().find("s") > -1:                                        # Check if season is "Special"
        item['season'] = "0"                                                          #
        item['episode'] = item['episode'][-1:]

    if ( item['file_original_path'].find("http") > -1 ):
        item['temp'] = True

    elif ( item['file_original_path'].find("rar://") > -1 ):
        item['rar']  = True
        item['file_original_path'] = os.path.dirname(item['file_original_path'][6:])

    elif ( item['file_original_path'].find("stack://") > -1 ):
        stackPath = item['file_original_path'].split(" , ")
        item['file_original_path'] = stackPath[0][8:]

    Search(item)

elif params['action'] == 'download':
    sub = Download(params["link"], params["lang"])
    listitem = xbmcgui.ListItem(label=sub.encode('utf-8'))
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=sub,listitem=listitem,isFolder=False)

xbmcplugin.endOfDirectory(int(sys.argv[1]))