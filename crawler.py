__author__ = 'Abhijeet Sharma'

import urllib2
import time
import robotparser
import re
import urlparse as up
from bs4 import BeautifulSoup
import frontier



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

def host_extract(url):
    parsed_url = up.urlparse(url)
    host_scheme = parsed_url[0]
    host_url = parsed_url[1]
    new_parsed_url = (host_scheme, host_url, "", "", "", "")
    url = up.urlunparse(new_parsed_url)
    return url

def polite_rules(url):
    host_url = host_extract(url)
    rp = robotparser.RobotFileParser()
    rp.set_url(host_url+'/robots.txt')
    rp.read()
    if rp.can_fetch("*", url):
        allowed = True
    else:
        allowed = False
    print "Url: ", url, "Allowed: ", allowed
    return allowed

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

front = frontier.FrontierQueue([seed_url1, seed_url2, seed_url3])
#front = frontier.FrontierQueue([seed_url1])
count = 0
explored = {}
in_link_dict = {}

while True:
    #being polite
    time.sleep(1)

    url, in_links = front.pop()

    in_link_dict[url] = in_links

    if explored.get(url) == None:
        visited = False
    else:
        print "Url already visited.Skipping... ", url
        visited = True

    allowed = polite_rules(url)

    if allowed and not visited:
        count += 1
        req = urllib2.Request(url)

        try: response = urllib2.urlopen(req)
        except urllib2.URLError as e:
            print e

        html = response.read()
        soup = BeautifulSoup(html)


        links = []

        for link in soup.find_all('a'):
            if link.get('href') is not None and link.get('href')[0]!='#':
                links.append(link.get('href'))

        head = str(soup.title.string)
        text = soup.get_text().encode('ascii','replace')

        with open(str(count)+".txt",'w') as f:
            f.write(text)
        print "write successful for url", url
        #with open("test_soup.txt",'w') as f:
         #   f.write(soup)

        links = links[:2]
        #real_url = response.geturl()

        for out_url in links:
            print "Before canonicalization ", out_url
            new_url = canonicalize(out_url, url)
            print "After canonicalization ", new_url
            if front.exists(new_url):
                print "Url exists in front (main)"
                front.update(new_url, url)
            elif explored.get(new_url) != None:
                print "Url doesn't exist in front (main) but exists in explored"
                in_link_dict[new_url].append(url)
            else:
                print "Url doesn't exist in front and doesn't exists in explored (new)"
                front.push(new_url, url)
                #in_link[new_url] = 1


            if explored.get(url) == None:
                explored[url] = set([new_url])
                print "new URL added in explored ",explored
            else:
                explored[url].add(new_url)
                print "old URL updated in explored ",explored

        #TODO write_file(head, text, explored[url], in_links)
        #TODO update_link_graph(url, links)
    print "Crawl for URL complete ", url
    print "\n\n"
    if count == 4:
        break




