__author__ = 'Abhijeet Sharma'

import urllib2
import time
import robotparser
import re
from bs4 import BeautifulSoup
import urlparse as up


def canonicalize(url, current_url):
    url = absolute_url(current_url, url)
    parsed_url = up.urlparse(url)
    new_scheme = parsed_url[0].lower()           # converting scheme to lowercase
    new_host_url = parsed_url[1].lower()         # converting netloc (host url) to lowercase
    port_list = re.findall(r':[0-9]+',new_host_url)
    for port_string in port_list:
        new_host_url = new_host_url.replace(port_string,"")
    new_path = parsed_url[2].replace("//","/") # replacing '//' with '/' in path
    new_params = parsed_url[3]
    new_query = parsed_url [4]
    new_fragment = ""                           # getting rid of fragments
    new_parsed_url = (new_scheme, new_host_url, new_path, new_params, new_query, new_fragment)
    url = up.urlunparse(new_parsed_url)
    return url

def absolute_url(current_url, url):
    url = up.urljoin(current_url, url)
    return url

'''1518 WORLD WAR 2
	http://www.history.com/topics/world-war-ii
	http://en.wikipedia.org/wiki/World_War_II
	http://en.wikipedia.org/wiki/List_of_World_War_II_battles_involving_the_United_States
	http://en.wikipedia.org/wiki/Military_history_of_the_United_States_during_World_War_II'''

'''an id, the URL, the HTTP headers, the page contents cleaned (with term positions), the raw html, and a list of all
in-links (known) and out-links for the page.'''

seed_url1 = 'http://en.wikipedia.org/wiki/World_War_II'
seed_url2 = 'http://en.wikipedia.org/wiki/List_of_World_War_II_battles_involving_the_United_States'
seed_url3 = 'http://en.wikipedia.org/wiki/Military_history_of_the_United_States_during_World_War_II'

# TODO frontier = Frontier()
frontier = [seed_url1, seed_url2, seed_url3]
count = 0

in_link = {}
out_link = {}


while True:
    #being polite
    time.sleep(1)

    url = frontier.pop()

    allowed = False
    host_url = host_extract(url)
    rp = robotparser.RobotFileParser()
    rp.set_url(host_url+'/robots.txt')
    rp.read()
    if rp.can_fetch("*", url):
        allowed = True

    if allowed == True:
        count += 1
        req = urllib2.Request(url)

        try: response = urllib2.urlopen(req)
        except URLError as e:
            print e

        html = response.read()
        soup = BeautifulSoup(html)

        head = str(soup.title.string)
        links = []

        for link in soup.find_all('a'):
            links.append(link.get('href'))

        text = soup.get_text().encode('ascii','replace')

        with open("test_text.txt",'w') as f:
            f.write(text)

        #with open("test_soup.txt",'w') as f:
         #   f.write(soup)


        real_url = response.geturl()


        for out_url in links:
            new_url = canonicalize(out_url)
            if new_url in frontier:
                in_link[new_url] += 1
            else:
                frontier.append(new_url)
                in_link[new_url] = 1
                out_link[new_url] = []
            if out_link.get(url) == None:
                out_link[url] = [new_url]
            else:
                out_link[url].append(new_url)


        #TODO write_file(text, url, html)
        #TODO update_link_graph(url, links)
    if count == 1:
        break




