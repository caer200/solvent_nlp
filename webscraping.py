from fuzzywuzzy import fuzz
import urllib
from urllib.request import build_opener, HTTPCookieProcessor
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import math
import time


class SIScraper:
    def __init__(self, doi, saveloc):
        self.doi = doi
        self.saveloc = saveloc
        self.filename = self.saveloc + "/" + self.doi.replace("/", "_") + ".pdf"
        
        
    def retrieveSI(self, pdfPref=True):
        # gets the html string that goes with a doi this is used to locate the SI
        self.html = self.getHTMLFromDOI()
        self.grURL = self.getRedirectUrlFromDOI()
        soup = BeautifulSoup(self.html)
        links = soup.find_all('a')
        siLocs = []
        
    
        # a list of keys and weights to determin which links on the page are likely to be the SI we want
        siIndictors = [{
            "txt": "supporting information",
            "w": 100
        }, {
            "txt": "supplementary files",
            "w": 100
        }, {
            "txt": "supplementary information",
            "w": 100
        }, {
            "txt": "supporting files",
            "w": 90
        }, {
            "txt": "supporting information",
            "w": 100
        }, {
            "txt": "support",
            "w": 50
        }, {
            "txt": " SI ",
            "w": 65
        }, {
            "txt": "SI",
            "w": 25
        },
            {
                "txt": self.doi,
                "w": 40
            }]
    
        # transform the keys and wieght to a list of dicts of different form
        for ind in siIndictors:
            tempHTML = self.html.lower()
            ind["txt"] = ind["txt"].lower()
            loc = tempHTML.find(ind["txt"])
            if (loc > -1):
                siLocs.append({"loc": loc, "w": ind["w"]})
    
        linkRes = []
        # loop through all links
        for link in links:
            try:
                # dont consider short links or anchor tags
                if (len(link['href']) < 2 or link['href'][0] == "#" or link['href'][0] == self.grURL):
                    continue
                linkLoc = self.html.lower().find(str(link).lower())
                for siLoc in siLocs:
                    linkRes.append({"dist": abs(siLoc["loc"] - linkLoc), "w": siLoc["w"], "url": link['href']})
            except KeyError as e:
                if (not str(e) == "'href'"):
                    print(type(e))
        scores = {}
        for lr in linkRes:
            hasFile = 1
            isDoiRel = 1
            isDoiOrg = 1
            isPDF = 1
            isProduct = 1
            # if it has a file extension such as .txt or .pdf it is likely the link we want
            if (lr['url'][-5:].find('.') < 2):
                hasFile = 10
            if (lr['url'][-5:].find('.pdf') > -1 and pdfPref):
                isPDF = 200
            # if it contains the doi it is likely to be the link we want
            if (self.isDoiMatch(lr['url'])):
                isDoiRel = 100
            if (lr['url'].find("https://doi.org/") > -1):
                isDoiOrg = 0
            if (lr['url'].find("product") > -1):
                isProduct = 0
            # score the link based on the weight divide by the distance between the key and the link
            # multiply by the has file and doi relivance weights
            s = (1 / lr['dist']) * (lr['w']) * hasFile * isDoiRel * isDoiOrg * isPDF * isProduct
            scores[str(s)] = lr['url']
        # get the URL with the highest score
        mk = -1
        for sk in scores.keys():
            if (mk < float(sk)):
                mk = float(sk)
        finUrlf = scores[str(mk)]
        # if the link is relative to the site not absolute make it absolute
        if (finUrlf.find('http') < 0):
            finUrlf = 'http://' + urllib.parse.urlparse(self.grURL).hostname + finUrlf
        ###
        # request the file and return its bytes
        ###
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
        self.siURL = finUrlf
        # uses the request library to enable easy creattion of an object that is like reading a file's bytes locally
        r = requests.get(finUrlf, headers=headers)
        if (not self.filename == -1):
            with open(self.filename, 'wb') as fi:
                fi.write(r.content)
    
    
    
    def getHTMLFromDOI(self):
        # format URL
        url = self.getUrlFromDoi()
        # request
        # creates a header as many webservers will through an error page if it cant write a cookie
        opener = build_opener(HTTPCookieProcessor())
        # create request headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', 'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8', 'Connection': 'keep-alive'}
        req = urllib.request.Request(url, headers=headers)
        r = opener.open(req, timeout=30)
        # r = urllib.request.urlopen(req);
        HTMLbytes = r.read()
        # change bytes to utf-8 string
        self.html = HTMLbytes.decode("utf8")
        return self.removeClutterTags()
    
    
    def removeClutterTags(self):
        # removes script tags and the content between them
        while (self.html.find("<script") > -1 and self.html.find("</script>") > self.html.find("<script")):
            temp1 = self.html[:self.html.find("<script")]
            temp2 = self.html[self.html.find("</script>") + len("</script>"):]
            self.html = temp1 + temp2
        # removes style tags and the content between them
        while (self.html.find("<style") > -1 and self.html.find("</style>") > self.html.find("<style")):
            temp1 = self.html[:self.html.find("<style")]
            temp2 = self.html[self.html.find("</style>") + len("</style>"):]
            self.html = temp1 + temp2
        return self.html
    
    def getUrlFromDoi(self):
        return "https://doi.org/" + self.doi
    
    
    def getRedirectUrlFromDOI(self):
        #format URL
        self.url = self.getUrlFromDoi()
        ##request
        #sets up a header to get through some sites that require a valid header
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive',
           }
        try:
            req = urllib.request.Request(self.url, headers=headers)
            r = urllib.request.urlopen(req)
            return r.url
        except Exception as e:
            if(str(e)=="HTTP Error 403: Forbidden"):
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--window-size=1920x1080")
                driver = webdriver.Chrome(options=chrome_options)
                driver.get(self.url)
                time.sleep(0.3)
                furl=driver.current_url
                driver.close()
                return furl
            else:
                raise e
    
    def isDoiMatch(self,link):
        if(link.find(self.doi.split("/")[0])>-1):
            linkDStem=link[link.find(self.doi.split("/")[0]):][:math.ceil(len(self.doi)*1.5)]
            return fuzz.ratio(linkDStem,self.doi)>65
        return False