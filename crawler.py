import logging
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from lxml import html
import requests
from urllib.parse import urljoin
import tokenizer


logger = logging.getLogger(__name__)


class Crawler:
    """
    This class is responsible for scraping urls from the next available link in frontier and adding the scraped links to
    the frontier
    """

    def __init__(self, frontier, corpus):
        self.frontier = frontier
        self.corpus = corpus
        self.tokenDict = {}
        self.urlWordCount = {}
        self.subdomains = {}
        self.traps = []
        self.domain = {}
        self.maxOutputLinks = 0
        self.maxOutputLinksName = ''
        self.urls = []
        self.i = 0

    def start_crawling(self):
        """
        This method starts the crawling process which is scraping urls from the next available link in frontier and adding
        the scraped links to the frontier
        """
   
        while self.frontier.has_next_url():
            url = self.frontier.get_next_url()
            logger.info("Fetching URL %s ... Fetched: %s, Queue size: %s", url, self.frontier.fetched, len(self.frontier))
            url_data = self.corpus.fetch_url(url)
            
            for next_link in self.extract_next_links(url_data):
                if self.is_valid(next_link, url_data):
                    if self.corpus.get_file_name(next_link) is not None:
                        self.frontier.add_url(next_link)
           
        
    
    def updateTokenDict(self, text):
        tokens = tokenizer.tokenize(text)
        self.tokenDict = tokenizer.computeWordFrequencies(self.tokenDict, tokens)
        
    def extract_next_links(self, url_data):
        """
        The url_data coming from the fetch_url method will be given as a parameter to this method. url_data contains the
        fetched url, the url content in binary format, and the size of the content in bytes. This method should return a
        list of urls in their absolute form (some links in the content are relative and needs to be converted to the
        absolute form). Validation of links is done later via is_valid method. It is not required to remove duplicates
        that have already been fetched. The frontier takes care of that.
        """
        outputLinks = []

        if url_data['final_url'] != None:
            url_data = self.corpus.fetch_url(url_data['final_url'])
        
        if url_data['http_code'] == 200:
            url = url_data['url']
            self.urls.append(url)
            
            soup = BeautifulSoup(url_data['content'],'lxml')
            
            text = soup.get_text()
            self.urlWordCount[url] = len(text.split())
            self.updateTokenDict(text)
            
            for link in soup.find_all('a'):
                outputLinks.append(urljoin(url, link.get('href')))
                
        else:
            url = url_data['url']
            self.traps.append(url)
        return outputLinks
    
    def trap_detection(self, url, url_data):
        parsed = urlparse(url)
        #extremely long url = trap

        if url in self.traps:
            return True
        if len(url) > 120:
            self.traps.append(url)
            return True
        
        #not http or https = trap
        if parsed.scheme not in set(["http", "https"]):
            self.traps.append(url)
            return True

        #Repeating directories = trap
        directories = parsed.path
        directories_list = directories.split('/')
        count = {}
        for d in directories_list:
            if d not in count:
                count[d] = 0
            else:
                count[d] +=1
        for v in count.values():
            if v > 1:
                self.traps.append(url)
                return True

         #compare every subdomain with the body
        parsed_domain = parsed.netloc + parsed.path
        string_count = 0

        url_data = self.corpus.fetch_url(url)
        if url_data['http_code'] == 200:
            soup = BeautifulSoup(url_data['content'],'html.parser')
        else:
            return True
        body = soup.body
        #Nearly duplicate URLS are traps, i.e. ~eppstein/pix, body of the website does not change; 90% similarity

        if parsed_domain not in self.domain:
            self.domain[parsed_domain] = set()
            if body is not None:
                for string in body.strings:
                    if string.isascii() and string != "\n" and string != " " and string is not None:
                        self.domain[parsed_domain].add(string)
        else:
            if body is not None:
                for string in body.strings:
                    if string.isascii() and string != "\n" and string != " " and string is not None:
                        if string in self.domain[parsed_domain]:
                            string_count +=1
                        if string_count > 0.9 * len(self.domain[parsed_domain]):
                            self.traps.append(url)
                            return True

        return url in self.traps



       

    def is_valid(self, url, url_data):
        """
        Function returns True or False based on whether the url has to be fetched or not. This is a great place to
        filter out crawler traps. Duplicated urls will be taken care of by frontier. You don't need to check for duplication
        in this method
        """

        
        valid = False;
        parsed = urlparse(url)
        if self.trap_detection(url,url_data):
            return False
        try:
            return ".ics.uci.edu" in parsed.hostname \
                   and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4" \
                                    + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
                                    + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
                                    + "|thmx|mso|arff|rtf|jar|csv" \
                                    + "|rm|smil|wmv|swf|wma|zip|rar|gz|pdf)$", parsed.path.lower())


        except TypeError:
            print("TypeError for ", parsed)
            return False
    
    def saveAnalatics(self):
        words = []
        with open('first50.txt', 'w') as file:
            i = 50
            for k,v in self.tokenDict.items():
                if i == 0:
                    break
                words.append(k)
                i = i-1
            file.writelines("% s\n" % w for w in words)
        
        with open('pageWordCount.txt', 'w') as file2:
            for k, v in sorted(self.urlWordCount.items(), key=lambda kv: kv[1], reverse=True):
                file2.write('number of words: %s %s\n' % (v, k))
                
        
        with open('traps.txt', 'w') as file3:
            for i in self.traps:
                file3.write('%s\n' % i)
        
        print(self.maxOutputLinksName,self.maxOutputLinks)
        with open('OutputLinks.txt', 'w') as file4:
            file4.write('%s has the most valid Output Links with %s links' % (self.maxOutputLinksName,self.maxOutputLinks))
        
        with open('subdomains.txt', 'w') as file5:
            for k,v in self.domain.items():
                #file5.write('%s\n' % k)
                file5.write('%s     %s\n' % (v, k))
                
        with open('urls.txt', 'w') as file6:
            for i in self.urls:
                file6.write('%s\n' % i)
