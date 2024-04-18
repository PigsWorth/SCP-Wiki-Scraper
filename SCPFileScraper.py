from bs4 import BeautifulSoup
import requests

# get001() \\ RETURN links list[set(String)], List of URLs found on the SCP-001 webpage.
#
# Returns a list[set()] of String literals found by the BeautifulSoup4 scanner that have the word 
# 'CODE NAME' in the text and 'proposal' in the 'href'(aka. URL) attribute.
def get001():
    urls = "https://scp-wiki.wikidot.com/scp-001"
    c = requests.get(urls)
    soup1 = BeautifulSoup(c.content, 'lxml')
    parent_url = "https://scp-wiki.wikidot.com"

    links = [parent_url + str(linkNUM) for linkNUM, 
            rawLink in [(a.get('href'), a.get_text()) for a in soup1.select('*[href*="proposal"]')]
            if "CODE NAME" in rawLink]
    return(links)

# linkFinder(int x) \\ PARAM x int, Article number \\ RETURN String, Article URL
#
# Generates a URL for an article webpage based on the inputted integer.
def linkFinder(x):
    if x > 1:
        return("https://scp-wiki.wikidot.com/scp-" + str(intToString(x)))
    elif x == 1:
        get001()

# intToString(int x) \\ PARAM x int, Article number \\ RETURN String,  Some amount of "0" + Article number.
#
# Convert an integer representation of the article number into it's string literal as shown on the website.
def intToString(x):
    if x in range(1, 10):
        return("00" + str(x))
    elif x in range(10, 99):
        return("0" + str(x))
    elif x in range(100, 10000):
        return(str(x))

# stringToInt(String x) \\ PARAM x String, Article URL/Article Number \\ RETURN int, Integer value of article number.
#
# Convert any variation of the "...SCP-XXX" String into it's integer counterpart.
def stringToInt(x):
    x = x[-6:]
    for i in x:
        if i.isdigit() == False:
            x = x[1:]
    x = x.lstrip("0")
    return int(x)

# next(String url) \\ PARAM url String, Base article URL \\ RETURN String, Base article URL + 1 to the number.
#
# Converts the URL into an integer representation, adds one, and converts back into a String URL.
def next(url):
    temp = stringToInt(url)
    temp += 1
    return linkFinder(temp)

# prev(String url) \\ PARAM url String, Base article URL \\ RETURN String, Base article URL - 1 to the number.
#
# Converts the URL into an integer representation, subtracts one, and converts back into a String URL.   
def prev(url):
    temp = stringToInt(url)
    temp -= 1
    return linkFinder(temp)

# =================================================================================================================
# Class designed to hold onto and provide both the string "00x" of a given article and the integer to represent it
# =================================================================================================================
class SCPFileScraper:
    masterDict = {}

    def __init__(self, articleNum):
        # Article number attribute.
        self.articleNum = articleNum

        # Article URL attribute.
        self.articleURL = linkFinder(articleNum)

        # # Article text content attribute. TODO Develop own visualization.
        # self.articleTxt = self.setText()

        # Outbound links dictionary attr set with method.
        self.setOutLinks()

        # Inbound links empty dictionary attr.
        self.inLinks = {}

        SCPFileScraper.masterDict[self.articleNum] = self

    def setText(self): # TODO Develop web visualization.
        c = requests.get(str(self.articleURL))
        bs = BeautifulSoup(c.content, 'lxml')
        tmp = bs.get_text()
        tmp = tmp[1200:-2400]
        id = str("Item #: SCP-" + str(intToString(self.articleNum)))
        while tmp[:len(id)] != id:
            tmp = tmp[1:]
        while tmp[-24:] != "Licensed under CC-BY-SA.":
            tmp = tmp[:-1]

        path = f"TextStorage/{self.articleNum}.txt"
        with open(path, 'w', encoding="utf_8") as txtFile:
            txtFile.write(tmp)
            txtFile.close
        
        return path


    def setOutLinks(self):
        # Dictionary of links pointing away from this article.
        currPageResults = []
        parent_url = 'https://scp-wiki.wikidot.com'
        c = requests.get(str(self.articleURL))
        bs = BeautifulSoup(c.content, 'lxml')

        #Searches the url from the queue to find urls that contain 'scp-' and aren't in the footer
        currPageResults = [parent_url + str(linkNUM) for linkNUM, rawLink in [(a.get('href'), a.get_text()) for a in bs.select('*[href*="scp-"]:not(.footer-wikiwalk-nav a)')] if "SCP-" in rawLink]

        #Filters the results for faulty results & false positives
        count = 3
        for c in range(count):
            for l in currPageResults: #Remove results if they:
                if str(self.articleURL) in l:
                    currPageResults.remove(l) #is a navbar link to the current page
                    count += 1
                elif str(prev(self.articleURL)) in l:
                    currPageResults.remove(l) #is a navbar link to the previous page                    
                    count += 1
                elif str(next(self.articleURL)) in l:
                    currPageResults.remove(l) # is a navbar link to the next page                    
                    count += 1
                elif l[-1].isdigit() == False:
                    currPageResults.remove(l) # ends in a number
                    count += 1
                elif l[28:61] == "https://scp-wiki.wikidot.com/scp-":
                    currPageResults[currPageResults.index(l)] = str(currPageResults[currPageResults.index(l)])[28:]
                    count += 1
                elif l[0:33] != 'https://scp-wiki.wikidot.com/scp-':
                    currPageResults.remove(l) # doesn't contain the parent url
                    count += 1

        if currPageResults != []:
            outDict = {}
            for link in currPageResults:
                key = "{link}".format(link = stringToInt(link))
                if key not in outDict:
                    outDict[key] = 1
                else:
                    outDict[key] += 1
            self.outLinks = outDict
        else:
            self.outLinks = {}

    def updateInLinks(self): # TODO Finish Method
        # Dictionary of links pointing to this article with strength.
        inDict = {}
        for article in SCPFileScraper.masterDict:
            for outLink in SCPFileScraper.masterDict[article].outLinks:
                if outLink == self.articleNum:
                    key = "{inLink}".format(inLink = article)
                    if key not in inDict:
                        inDict[key] = 1
                    else:
                        inDict[key] += 1
        self.inLinks = inDict


    def __str__(self):
        return (f"SCP-{intToString(self.articleNum)}\nOutbound Links:\n{self.outLinks}\nInbound Links:\n{self.inLinks}")
    
if __name__ == "__main__":
    for i in range(2,5):
        tmp = SCPFileScraper(i)
        print(tmp)