# -*- coding: utf-8 -*-
# coding: utf-8

import re
import os
import sys
# import xbmc
import requests

import zipfile
# from unrar import rarfile


import shutil
# import xbmcvfs
# import xbmcaddon
# import xbmcgui,xbmcplugin
from bs4 import BeautifulSoup

# reload(sys)
# sys.setdefaultencoding('utf-8')


headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Accept-Encoding': 'gzip, deflate, sdch, br',
           'Accept-Language': 'zh-CN,zh;q=0.8',
           'Connection': 'keep-alive',
           'Upgrade-Insecure-Requests': '1',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}

assrt_API = 'http://assrt.net/sub/?searchword=%s'
assrt_BASE = 'http://assrt.net/'
FLAG_DICT = {'china':'简', 'hongkong':'繁', 'uk':'英', 'jollyroger':'双语'}
exts = [".srt", ".sub", ".smi", ".ssa", ".ass" ]

__temp__ = sys.path[0]

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

    if file.lower().endswith('zip'):
        zipFile = zipfile.ZipFile(file,'r')
        for names in zipFile.namelist():
            if type(names) == str and names[-1] != '/':
                utf8name = names.decode('gbk')
                data = zipFile.read(names)
                with open(path+utf8name, 'wb') as f: f.write(data)
            else:
                zipFile.extract(names,path)
        return getFileList(path)

    if file.lower().endswith('rar'):
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
                if '语言' in x.getText():
                    if '简' in x.getText() or '繁' in x.getText() or '双语' in x.getText():
                        lang = '简'
                        language_name = 'Chinese'
                        language_flag = 'zh'
                    elif '英' in x.getText():
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
                if i.getText() == '1' or i.getText() == '>' or '/' in i.getText(): continue
                lists += getUriLinks(url, int(i.getText()))
                print('获取到页码：',int(i.getText()))
    return lists

def Search():
    subtitles_list = []

    url = assrt_API % '终结者'
    # url = assrt_API % '最终幻想15：王者之剑'
    try:
        print(getUriLinks(url))
        # print(len(getUriLinks(url,5)))
        res = requests.get(url, headers=headers)
    except:
        return
    else:
        soup = BeautifulSoup(res.content,'html.parser')
        divs = soup.find_all('div',class_='subitem')
        page = soup.find('div',class_='pagelinkcard')
        for i in divs:
            title = i.find('a',class_='introtitle')
            if title is None: continue
            name = title.getText().strip().split('/')[-1]
            link = title.get('href')
            content = i.find('div',id='sublist_div').find_all('span')
            for x in content:
                if '语言' in x.getText():
                    if '简' in x.getText() or '繁' in x.getText() or '双语' in x.getText():
                        lang = '简'
                        language_name = 'Chinese'
                        language_flag = 'zh'
                    elif '英' in x.getText():
                        lang = '英'
                        language_name = 'English'
                        language_flag = 'en'
                    else:
                        lang = '未知'
                        language_name = 'Chinese'
                        language_flag = 'zh'

            subtitles_list.append({"language_name":language_name, "filename":name, "link":link, "language_flag":language_flag, "rating":"0", "lang":lang})
    return subtitles_list
    # if subtitles_list:
    #     for it in subtitles_list:
    #         listitem = xbmcgui.ListItem(label=it["language_name"],
    #                               label2=it["filename"],
    #                               iconImage=it["rating"],
    #                               thumbnailImage=it["language_flag"]
    #                               )

    #         listitem.setProperty( "sync", "false" )
    #         listitem.setProperty( "hearing_imp", "false" )

    #         url = "plugin://%s/?action=download&link=%s&lang=%s" % (__scriptid__,
    #                                                                     it["link"],
    #                                                                     it["lang"]
    #                                                                     )
    #         xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=False)

def Download(url):
    # try: shutil.rmtree(__temp__)
    # except: pass
    # try: os.makedirs(__temp__)
    # except: pass

    lists = []
    exts = [".srt", ".sub", ".smi", ".ssa", ".ass" ]
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
        # xbmc.log(tempfile)
        with open(tempfile, "wb") as subFile: subFile.write(res.content)
        # xbmc.sleep(100)
        if fileName.split('.')[-1].lower() in ('zip','rar'):
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



# unZip('subtitles.rar')
url = Search()
# print(url[0]['link'])
# Download(url[0]['link'])
# Download('http://www.zimuku.cn/detail/71607.html')

# print os.path.join( __temp__, 'temp')