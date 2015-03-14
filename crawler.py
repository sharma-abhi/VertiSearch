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

def policy_rules(url):
    host_url = host_extract(url)
    rp = robotparser.RobotFileParser()
    rp.set_url(host_url+'/robots.txt')
    rp.read()
    if rp.can_fetch("*", url):
        allowed = True
    else:
        allowed = False
    #print "Url: ", url, "Allowed: ", allowed
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
seed_url4 = 'http://www.history.com/topics/world-war-ii'

front = frontier.FrontierQueue([seed_url1, seed_url2, seed_url3, seed_url4])
#front = frontier.FrontierQueue([seed_url1])
count = 0
explored = {}
in_link_dict = {}
opener = urllib2.build_opener()
headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:10.0.1) Gecko/20100101 Firefox/10.0.1',
}

opener.addheaders = headers.items()

while True:
    #being polite
    time.sleep(1)
    if front.isEmpty():
        print "QUEUE EMPTY"
        break
    else:
        url, in_links = front.pop()
    print count, "Crawl started for URL ", url
    in_link_dict[url] = in_links

    if explored.get(url) == None:
        visited = False
    else:
        #print "Url already visited.Skipping... ", url
        visited = True

    allowed = policy_rules(url)

    if allowed and not visited:
        count += 1



        #req = urllib2.Request(url)
        #try: response = urllib2.urlopen(req)
        try: response = opener.open(url)
        except urllib2.URLError as e:
            print "Error: ", e," for URL: ", url
            continue

        html = response.read()
        header_info = response.info().dict['content-type']

        if len(re.findall('text/html',header_info)) == 0:
            print "Link not text/html.Skipping..."
            continue

        soup = BeautifulSoup(html)

        if soup.title == None:
            head = "<No Title>"
        else:
            head = soup.title.string.encode('ascii','ignore')

        text_list = [''.join(s.findAll(text=True)) for s in soup.find_all('p')]
        body_text = '.'.join(text_list).encode('ascii','ignore')
        if soup.find("table") == None:
            table_text = ''
        else:
            table_text = soup.find("table").get_text().encode('ascii','ignore')

        text = body_text + table_text
        text = text.replace("\n",' ')

        with open("output/"+"VS"+str(count)+".txt",'w') as f:
            f.write(text)
        #print "write successful for url", url

        links = []

        for link in soup.find_all('a'):
            if link.get('href') is not None  and link.get('href') != '' and link.get('href')[0]!='#':
                links.append(link.get('href'))

        #links = links[:2]

        for out_url in links:
            #print "Before canonicalization ", out_url
            new_url = canonicalize(out_url, url)
            #print "After canonicalization ", new_url
            if front.exists(new_url):
                #print "Url exists in front (main)"
                front.update(new_url, url)
            elif explored.get(new_url) != None:
                #print "Url doesn't exist in front (main) but exists in explored"
                in_link_dict[new_url].add(url)
            else:
                #print "Url doesn't exist in front and doesn't exists in explored (new)"
                front.push(new_url, url)


            if explored.get(url) == None:
                explored[url] = set([new_url])
                #print "new URL added in explored ",explored
            else:
                explored[url].add(new_url)
                #print "old URL updated in explored ",explored

        #TODO write_file(head, text, explored[url], in_links)
        #TODO update_link_graph(url, links)
        #print count," Crawl for URL complete ", url
        #print "\n\n"
        if count == 10000:
            break
    else:
        print "Skipping URL: ",url



