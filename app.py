from flask import Flask, render_template
import cloudscraper
import json

app = Flask(__name__, template_folder='templates', static_folder='static')

def getChapterURL(mangaName, chapterCode):
    chapterDirectory = str(int(chapterCode[0:1]))
    chapterNumber = str(int(chapterCode[1:-1]))
    chapterIndex = str(int(chapterCode[-1]))
    return "https://mangasee123.com/read-online/" + mangaName + "-chapter-" + chapterNumber + "." + chapterIndex + "-index-" + chapterDirectory + ".html"

def getTextBetweenTwoStringsFixed(string, start, end):
    return string.text[string.text.find(start) + len(start):string.text.find(end)]

def getRequestResponse(url):
    scraper = cloudscraper.create_scraper()
    while(True):
        try:
            response = scraper.get(url)
            break
        except:
            pass
    return response

def getMangaSeedURL(mangaName):
    mangaURL = "https://mangasee123.com/manga/" + mangaName
    response = getRequestResponse(mangaURL)
    mangaSeed = getTextBetweenTwoStringsFixed(response, '{"Chapter":"', '","Type":"')
    return getChapterURL(mangaName, mangaSeed)

def getChapterList(chapterURL):
    response = getRequestResponse(chapterURL)
    scrappedList = getTextBetweenTwoStringsFixed(response, "vm.CHAPTERS = ", "			vm.IndexName =")[0:-3]
    scrappedList = json.loads(scrappedList)
    return scrappedList

def getPageList(mangaName, chapterNumber, chapterList, chapterListIndexes):
    realChapterNumber = chapterListIndexes[chapterNumber]
    chapterJSON = chapterList[int(realChapterNumber)]
    chapterDirectory = str((chapterJSON["Directory"]))
    chapterNumber = str(int(chapterJSON["Chapter"][1:-1]))
    chapterIndex = str(int(chapterJSON["Chapter"][-1]))
    pageNumberTotal = int(chapterJSON["Page"])
    chapterURL = getChapterURL(mangaName, chapterJSON["Chapter"])
    response = getRequestResponse(chapterURL)
    host = getTextBetweenTwoStringsFixed(response, 'vm.CurPathName = "', 'vm.CHAPTERS = ').rstrip()[0:-2]
    extension = getTextBetweenTwoStringsFixed(response, str("{{vm.PageImage(Page)}}."), 'on-error-src=').rstrip()[0:-1]
    pageList = []
    for i in range(pageNumberTotal):
        pageList.append(getChapterPages(mangaName, chapterJSON, i + 1, host, extension))
    return pageList

def getChapterPages(mangaName, chapterJSON, pageNumber, host, extension):
    imageURL = "https://" + host + "/manga/"+ mangaName + "/" + str(chapterJSON["Directory"]) + "/" + str(int(chapterJSON["Chapter"][1:-1])).zfill(4) + "-" + str(pageNumber).zfill(3) + "." + extension
    return imageURL

def getChapterImages(mangaName, chapterNumber, pageNumber, chapterList, chapterListIndexes):
    realChapterNumber = chapterListIndexes[chapterNumber]
    print(realChapterNumber)
    chapterJSON = chapterList[int(realChapterNumber)]
    chapterDirectory = str((chapterJSON["Directory"]))
    chapterNumber = str(int(chapterJSON["Chapter"][1:-1]))
    chapterIndex = str(int(chapterJSON["Chapter"][-1]))
    pageNumberTotal = int(chapterJSON["Page"])
    chapterURL = getChapterURL(mangaName, chapterJSON["Chapter"])
    response = getRequestResponse(chapterURL)
    host = getTextBetweenTwoStringsFixed(response, 'vm.CurPathName = "', 'vm.CHAPTERS = ').rstrip()[0:-2]
    extension = getTextBetweenTwoStringsFixed(response, str("{{vm.PageImage(Page)}}."), 'on-error-src=').rstrip()[0:-1]
    return getChapterPages(mangaName, chapterJSON, pageNumber, host, extension)

@app.route('/readManga/<mangaName>/<int:chapterNumber>/<int:pageNumber>')
def index(mangaName, chapterNumber, pageNumber):
    mangaSeedURL = getMangaSeedURL(mangaName)
    chapterList = getChapterList(mangaSeedURL)
    chapterJSON = chapterList[int(chapterNumber - 1)]
    chapterDirectory = str((chapterJSON["Directory"]))
    chapterNumber = str(int(chapterJSON["Chapter"][1:-1]))
    print(chapterNumber)
    chapterIndex = str(int(chapterJSON["Chapter"][-1]))
    pageNumberTotal = int(chapterJSON["Page"])
    chapterListIndexes = [i for i in range(0, len(chapterList))]
    chapterImagePrevious = pageNumber - 1
    chapterImageNext = pageNumber + 1
    chapterURL = getChapterURL(mangaName, chapterJSON["Chapter"])
    response = getRequestResponse(chapterURL)
    host = getTextBetweenTwoStringsFixed(response, 'vm.CurPathName = "', 'vm.CHAPTERS = ').rstrip()[0:-2]
    extension = getTextBetweenTwoStringsFixed(response, str("{{vm.PageImage(Page)}}."), 'on-error-src=').rstrip()[0:-1]
    imageURL = "https://" + host + "/manga/"+ mangaName + "/" + str(chapterJSON["Directory"]) + "/" + str(int(chapterJSON["Chapter"][1:-1])).zfill(4) + "-" + str(pageNumber).zfill(3) + "." + extension
    chapterImage = imageURL
    print(imageURL)
    return render_template('reader.html', chapterImage = chapterImage, chapterImageNext = chapterImageNext, chapterImagePrevious = chapterImagePrevious)