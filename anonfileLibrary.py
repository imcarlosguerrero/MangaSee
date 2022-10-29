import cloudscraper
import requests
import json
import re
from time import sleep

def getTextBetweenTwoStrings(string, start, end):
    return string.text[string.text.find(start) + len(start):string.text.rfind(end)]

def getRedirectURL(AnonfileURL):
    scraper = cloudscraper.create_scraper(browser='chrome', interpreter='nodejs')
    response = scraper.get(AnonfileURL)
    cdn = getTextBetweenTwoStrings(response, 'class="btn btn-primary btn-block"', '">                    <img')
    cdnURL = re.findall(r'(https?://\S+)', cdn)
    return cdnURL[0]    

def getAnonfileURL(anonfileUploadResponse):
    return json.loads(anonfileUploadResponse.text)["data"]["file"]["url"]["short"]

def getAnonfileUploadResponse(fileName, fileExtension):
    while(True):
        try:
            scraper = cloudscraper.create_scraper(browser='chrome', interpreter='nodejs')
            AnonfileUploadResponse = scraper.post("https://api.anonfiles.com/upload", files={"file": open(str("Mangas/" + fileName) + "." + str(fileExtension), "rb")})
        except Exception as e:
            print(e)
            print("\nError al intentar subir el archivo, intentando de nuevo...")
        else:
            return AnonfileUploadResponse

def isURLReady(AnonfileURL):
    counter = 0
    redirectURL = ""
    while(True):
        while(True):
            try:
                redirectURL = getRedirectURL(AnonfileURL)
                print("\n", redirectURL)
                statusCode = requests.get(redirectURL).status_code
            except Exception as e:
                print(e)
                sleep(5)
                print("\nEl servidor ha fallado...")
            else:    
                break
                
        if(statusCode == 200):
                print("\nEl archivo esta listo para descarga:", redirectURL)
                return True
        else:
            counter += 1
            if(counter == 50):
                print("\nLimite de espera alcanzado, reintentando...")
                return False
            sleep(5)

def uploadAnonfile(fileName, fileExtension):
    while(True):
        print("\nSubiendo archivo al servidor...")
        anonfileUploadResponse = getAnonfileUploadResponse(fileName, fileExtension)
        print(anonfileUploadResponse)
        anonfileURL = getAnonfileURL(anonfileUploadResponse)
        print("\nURL Manual", anonfileURL)
        return anonfileURL