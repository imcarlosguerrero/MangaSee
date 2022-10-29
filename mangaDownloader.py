from ParallelFunction import parallelFunction
from anonfileLibrary import uploadAnonfile
import cloudscraper
import shutil
import json
import sys
import os

def downloadManga(mangaName):
    mangaExistence = checkMangaExistence(mangaName)
    if(mangaExistence == True):
        mangaURL = getMangaURL(mangaName)
        print(mangaURL)
        return True
    else:
        mangaSeedURL = getMangaSeedURL(mangaName)
        chapterList = getChapterList(mangaSeedURL)
        createFolder("Mangas" + "/" + mangaName)
        chapterListIndexes = [i for i in range(0, len(chapterList))]     
        parallelFunction(getChapterImages, chapterListIndexes, 3, [mangaName, chapterList])
        zipFolder("Mangas" + "/" + mangaName)
        mangaURL = uploadAnonfile(mangaName, "zip")
        saveMangaURL(mangaName, mangaURL)
        return True

def getAlreadyDownloadedMangas():
    listdirs = os.listdir("Mangas")
    alreadyDownloadedMangas = []
    return alreadyDownloadedMangas

def getAllMangaNames():
    with open("fullDirectory.json") as f:
            data = json.load(f)
    f.close()
    mangaNames = []
    for i in range(len(data["Directory"])):
        mangaName = data["Directory"][i]["i"]
        mangaNames.append(mangaName)
    print(mangaNames)
    return mangaNames[:100]

def createFolder(folderName):
    try:
        os.makedirs(folderName)
    except OSError:
        pass

def checkMangaExistence(mangaName):
    jsonPath = os.path.abspath("urls.json")
    with open(jsonPath) as f:
        data = json.load(f)
    f.close()
    for i in range(len(data)):
        if(mangaName in data[i]):
            return True
    return False

def getMangaURL(mangaName):
    jsonPath = os.path.abspath("urls.json")
    with open(jsonPath) as f:
        data = json.load(f)
    f.close()
    for i in range(len(data)):
        if(mangaName in data[i]):
            return data[i][mangaName]

def saveMangaURL(mangaName, mangaURL):
    jsonPath = os.path.abspath("urls.json")
    with open(jsonPath) as f:
        data = json.load(f)
    data.append({str(mangaName):str(mangaURL)})
    f.close()
    with open(jsonPath, "w") as f:
        json.dump(data, f)
    f.close()   

def zipFolder(folderName):
    if(os.path.exists("Mangas/" + folderName + ".zip")):
        return True
    shutil.make_archive(folderName, 'zip', folderName)
    
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

def getChapterURL(mangaName, chapterCode):
    chapterDirectory = str(int(chapterCode[0:1]))
    chapterNumber = str(int(chapterCode[1:-1]))
    chapterIndex = str(int(chapterCode[-1]))
    return "https://mangasee123.com/read-online/" + mangaName + "-chapter-" + chapterNumber + "." + chapterIndex + "-index-" + chapterDirectory + ".html"

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

def getChapterImages(i, masterVariables):
    mangaName = masterVariables[0]
    chapterList = masterVariables[1]
    chapterJSON = chapterList[i]
    
    chapterDirectory = str((chapterJSON["Directory"]))
    chapterNumber = str(int(chapterJSON["Chapter"][1:-1]))
    chapterIndex = str(int(chapterJSON["Chapter"][-1]))
    pageNumber = str(int(chapterJSON["Page"]))
    if(int(chapterIndex) == 0):
        chapterFolderName = chapterDirectory + " " + chapterNumber
    else:
        chapterFolderName = chapterDirectory + " " + chapterNumber + "." + chapterIndex
        
    createFolder("Mangas" + "/" + mangaName + "/" + chapterFolderName)
    downloadedPages = len(os.listdir("Mangas" + "/" + mangaName + "/" + chapterFolderName))
    if(downloadedPages == int(pageNumber)):
        return True
    else:  
        pageNumber = int(chapterJSON["Page"])
        chapterPageNumbers = [i for i in range(1, pageNumber + 1)]
        #pages Download
        chapterURL = getChapterURL(mangaName, chapterJSON["Chapter"])
        response = getRequestResponse(chapterURL)
        host = getTextBetweenTwoStringsFixed(response, 'vm.CurPathName = "', 'vm.CHAPTERS = ').rstrip()[0:-2]
        extension = getTextBetweenTwoStringsFixed(response, str("{{vm.PageImage(Page)}}."), 'on-error-src=').rstrip()[0:-1]
        parallelFunction(downloadChapterPages, chapterPageNumbers, 5, [mangaName, chapterFolderName, host, extension, chapterJSON])
        return True
    
def downloadChapterPages(chapterPage, masterVariables):
    mangaName = masterVariables[0]
    chapterFolderName = masterVariables[1]
    host = masterVariables[2]
    extension = masterVariables[3]
    chapterJSON = masterVariables[4]
    
    if(os.path.exists("Mangas" + "/" + mangaName + "/" + chapterFolderName + "/" + str(chapterPage) + '.' + extension)):
        return True
    else:
        imageURL = "https://" + host + "/manga/"+ mangaName + "/" + str(chapterJSON["Directory"]) + "/" + str(int(chapterJSON["Chapter"][1:-1])).zfill(4) + "-" + str(chapterPage).zfill(3) + "." + extension
        pageImage = getRequestResponse(imageURL)
        with open("Mangas" + "/" + mangaName + "/" + chapterFolderName + "/" + str(chapterPage) + '.' + extension, 'wb') as handler:
            handler.write(pageImage.content)
        handler.close()
        print("Downloaded " + mangaName + " " + chapterFolderName + " " + str(chapterPage) + '.' + extension)
        if(os.path.exists("Mangas" + "/" + mangaName + "/" + chapterFolderName + "/" + str(chapterPage) + '.' + extension)):
            return True
        else:
            return False
    return True

if __name__ == '__main__':
    args = list(sys.argv)
    args.pop(0)

    if(len(args) == 1):
        downloadManga(args[0])

    elif(args[0] == "download" and args[1] == "all"):
        mangaNames = getAllMangaNames()
        parallelFunction(downloadManga, mangaNames, 10)

    elif(args[0] == "update" and args[1] == "all"):
        alreadyDownloadedMangas = getAlreadyDownloadedMangas()
        parallelFunction(downloadManga, alreadyDownloadedMangas, len(alreadyDownloadedMangas))

    else:
        mangaNames = args[0:]
        parallelFunction(downloadManga, mangaNames, len(mangaNames))