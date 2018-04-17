from bs4 import BeautifulSoup
from urllib import request
import shutil,os

def makesoup(url):
    page = request.urlopen(url).read()
    soup = BeautifulSoup(page,"html.parser")
    return soup
furl = "https://bingwallpaper.com"
fold = "BingWallpapers"
try:
    if not os.path.exists(fold):
        os.makedirs(fold)

    list = os.listdir()

    soup = makesoup(furl)
    srclist = set()
    black = []
    print(list)
    for i in soup.findAll('img'):
        img = i["src"].split('/')[-1]
        if img not in list and img not in black:
            srclist.add(i['src'])

        else:
            try:
                list.remove(img)
                black.append(img)
            except:
                pass

    for ent in list:
        if(not str(ent).endswith(".py") and str(ent)!=fold and not str(ent).endswith(".exe")):
            try:
                shutil.move(ent,fold)
            except:
                os.unlink(ent)

    for i in srclist:
        if i[0]== '/':
            continue
        imagefile = open(i.split('/')[-1],"wb")
        imagefile.write(request.urlopen(i).read())
        imagefile.close()
        print(i)
    print("Done")

except:
    print("None")