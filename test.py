# -*- coding: utf-8 -*-
# coding: utf-8

import re
import os
import sys
# import xbmc
import urllib
import urllib2

import zipfile
from unrar import rarfile

# import requests
import shutil
# import xbmcvfs
# import xbmcaddon
# import xbmcgui,xbmcplugin
from bs4 import BeautifulSoup




reload(sys)
sys.setdefaultencoding('utf-8')


headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Accept-Encoding': 'gzip, deflate, sdch, br',
           'Accept-Language': 'zh-CN,zh;q=0.8',
           'Connection': 'keep-alive',
           'Upgrade-Insecure-Requests': '1',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}



ZIMUKU_API = 'http://www.zimuku.cn/search?q=%s'
ZIMUKU_BASE = 'http://www.zimuku.cn'
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

#解压缩Zip到指定文件夹
def extractZip(zfile, path):
    z = ZFile(zfile)
    z.extract_to(path)
    z.close()

#解压缩rar到指定文件夹
def extractRar(zfile, path):
    rar_command1 = "WinRAR.exe x -ibck %s %s" % (zfile, path)
    rar_command2 = r'"C:\WinRAR.exe" x -ibck %s %s' % (zfile, path)
    if os.system(rar_command1) == 0:
        print "Path OK."
    else:
        if os.system(rar_command2) != 0:
            print "Error."
        else:
            print "Exe OK"

def unZip(filepath):
    path  = __temp__ + '/subtitles/'
    if os.path.isdir(path): shutil.rmtree(path)
    if not os.path.isdir(path): os.mkdir(path)

    if filepath.lower().endswith('zip'):
        zip_file = zipfile.ZipFile(filepath,'r')
        for names in zip_file.namelist():
            if type(names) == str and names[-1] != '/':
                utf8name = names.decode('gbk')
                data = zip_file.read(names)
                fo = open(path+utf8name, "w")
                fo.write(data)
                fo.close()
            else:
                zip_file.extract(names,path)
        return getFileList(path)
    if filepath.lower().endswith('rar'):
        zip_file = rarfile.RarFile(filepath,'r')
        for names in zip_file.namelist():
            if type(names) == str and names[-1] != '/':
                utf8name = names.decode('gbk')
                data = zip_file.read(names)
                fo = open(path+utf8name, "w")
                fo.write(data)
                fo.close()
            else:
                zip_file.extract(names,path)
        return getFileList(path)



def Search():
    subtitles_list = []

    # log( __name__ ,"Search for [%s] by name" % (os.path.basename( item['file_original_path'] ),))
    # if item['mansearch']:
    #     url = ZIMUKU_API % '最终幻想15：王者之剑'
    # else:
    url = ZIMUKU_API % 'the croods'
    # url = ZIMUKU_API % '最终幻想15：王者之剑'
    try:
        socket = urllib.urlopen(url)
        data = socket.read()
        socket.close()
        soup = BeautifulSoup(data,'html.parser')
    except:
        return
    results = soup.find_all("div", class_="item prel clearfix")
    for it in results:
        moviename = it.find("div", class_="title").a.text.encode('utf-8')
        iurl = it.find("div", class_="title").a.get('href').encode('utf-8')
        movieurl = '%s%s' % (ZIMUKU_BASE, iurl)
        try:
            socket = urllib.urlopen(movieurl)
            data = socket.read()
            socket.close()
            soup = BeautifulSoup(data,'html.parser').find("table", class_="table")
            soup = soup.find("tbody")
        except:
            return
        subs = soup.find_all("tr")
        # print(subs)
        for sub in subs:

            name = sub.a.text.encode('utf-8')

            flag = sub.img.get('src').split('/')[-1].split('.')[0].encode('utf-8')
            lang = FLAG_DICT.get(flag,'unkonw')
            link = '%s%s' % (ZIMUKU_BASE, sub.a.get('href').encode('utf-8'))

            if lang == '英':
                subtitles_list.append({"language_name":"English", "filename":name, "link":link, "language_flag":'en', "rating":"0", "lang":lang})
            else:
                subtitles_list.append({"language_name":"Chinese", "filename":name, "link":link, "language_flag":'zh', "rating":"0", "lang":lang})
    return subtitles_list
    for i in subtitles_list:
        print i['filename']
        print i["link"]
        # extension = i['filename'].split('.')[-1]
        # if extension in ['zip','Zip','rar','RAR']:
        #     url = "plugin://%s/?action=download&link=%s&lang=%s&ext=%s" % ('__scriptid__',i["link"],i["lang"],extension)
        # else:
        #     url = "plugin://%s/?action=download&link=%s&lang=%s" % ('__scriptid__',i["link"],i["lang"])
        # print url
        # for j in i: print j,i[j]
    # print subtitles_list
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

    subtitle_list = []
    exts = [".srt", ".sub", ".smi", ".ssa", ".ass" ]
    try:
        socket = urllib.urlopen(url)
        data = socket.read()
        soup = BeautifulSoup(data,'html.parser')
        url = soup.find("li", class_="li dlsub").a.get('href').encode('utf-8')

        socket = urllib.urlopen(url)
        data = socket.read()
        soup = BeautifulSoup(data,'html.parser')
        div = soup.find('div',class_='down clearfix')
        li = div.find('li')
        headers['Referer'] = url

        req = urllib2.Request(li.a.get('href'),headers=headers)
        resp = urllib2.urlopen(req)

        print(resp.headers['Content-Disposition'].replace('"','').split('=')[1])
        print(resp.geturl())

        socket = urllib.urlopen(resp.geturl())
        data = socket.read()
        socket.close()
    except:
        return []

    if len(data) < 1024:return []

    tempfile = os.path.join(__temp__, "subtitles.zip")

    with open(tempfile, "wb") as subFile: subFile.write(data)
    subFile.close()
    # xbmc.sleep(500)
    lists = unZip(tempfile)
    lists = [i for i in lists if i.split('.')[-1] in exts]




    return lists
    path = __temp__
    dirs, files = xbmcvfs.listdir(path)
    if len(dirs) > 0:
        path = os.path.join(__temp__, dirs[0].decode('utf-8'))
        dirs, files = xbmcvfs.listdir(path)
    list = []
    for subfile in files:
        if (os.path.splitext( subfile )[1] in exts):
            list.append(subfile.decode('utf-8'))
    if len(list) == 1:
        subtitle_list.append(os.path.join(path, list[0]))
    else:
        sel = xbmcgui.Dialog().select('请选择压缩包中的字幕', list)
        if sel == -1:
            sel = 0
        subtitle_list.append(os.path.join(path, list[sel]))

    return subtitle_list


unZip('subtitles.rar')
# url = Search()
# print(url)
# Download(url[0]['link'])
# Download('http://www.zimuku.cn/detail/71607.html')

# print os.path.join( __temp__, 'temp')