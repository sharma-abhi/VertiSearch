__author__ = 'abhijeet'

import re
import urlparse as up

class Canonicalizer():

    def  __init__(self):
        #nothing here for now
        pass

    # function to canonicalize urls
    # INPUT:  url -> the current out link which will be canonicalized
    #         current_url -> the current url being crawled
    # OUTPUT: url -> canonicalized url
    '''
    1. Convert the scheme and host to lower case:
        HTTP://www.Example.com/SomeFile.html -> http://www.example.com/SomeFile.html
    2. Remove port 80 from http URLs, and port 443 from HTTPS URLs:
        http://www.example.com:80 -> http://www.example.com
    3. Make relative URLs absolute: if you crawl http://www.example.com/a/b.html and
        find the URL ../c.html -> http://www.example.com/c.html.
    4. Remove the fragment, which begins with #:
        http://www.example.com/a.html#anything -> http://www.example.com/a.html
    5. Remove duplicate slashes:
        http://www.example.com//a.html -> http://www.example.com/a.html'''

    def canonicalize(self, url, current_url):
        url = self.absolute_url(url, current_url)
        parsed_url = up.urlparse(url)
        new_scheme = parsed_url[0].lower()           # converting scheme to lowercase
        new_host_url = parsed_url[1].lower()         # converting netloc (host url) to lowercase
        port_list = re.findall(r':[0-9]+',new_host_url)
        for port_string in port_list:
            new_host_url = new_host_url.replace(port_string,"")

        new_path = parsed_url[2].replace("//","/") # replacing '//' with '/' in path
        new_params = ""                             # getting rid of params
        new_query = ""                              # getting rid of queries
        new_fragment = ""                           # getting rid of fragments
        new_parsed_url = (new_scheme, new_host_url, new_path, new_params, new_query, new_fragment)
        url = up.urlunparse(new_parsed_url)         # putting it back together
        return url

    # function to make partial urls absolute
    # INPUT:  url -> the current out link
    #         current_url -> the current url being crawled
    # OUTPUT: url -> absolute url
    # EXAMPLES:
    # absolute_url('/wiki/World_War_II','http://www.wikipedia.com') ->
    # 'http://www.wikipedia.com/wiki/World_War_II'
    def absolute_url(self, url, current_url):
        url = up.urljoin(current_url, url)
        return url