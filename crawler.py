__author__ = 'Abhijeet Sharma'

import urllib2
import time
from datetime import datetime
import re
import urlparse as up
from bs4 import BeautifulSoup
from bs4 import element
import frontier
import robotexclusionrulesparser as rerp
import json
import relevancechecker as rc
from canonicalization import Canonicalizer
from elasticsearch import Elasticsearch

def is_present(es, docNo):
    try: req = es.get(index = 'vs_dataset', doc_type = 'document', id = docNo, fields = ['text'])
    except:
        return False
    else:
        return True

def host_extract(url):
    parsed_url = up.urlparse(url)
    host_scheme = parsed_url[0]
    host_url = parsed_url[1]
    new_parsed_url = (host_scheme, host_url, "", "", "", "")
    url = up.urlunparse(new_parsed_url)
    return url

def policy_rules(url):
    global banned_domains
    
    host_url = host_extract(url)
   
    # Excluding sites like Facebook, Amazon, Linkedin, etc.  
    for domain in banned_domains:
        if domain in host_url:
            print "Banned Domain", domain ," Skipping..."
            return False
    
    rp = rerp.RobotExclusionRulesParser()
    try_count = 0
    while try_count < 2:
        try: rp.fetch(host_url+'/robots.txt')
        except urllib2.URLError as e:
            print "Error: ", e," for URL: ", url.encode('ascii','ignore')
            try_count += 1
        except UnicodeError as e:
            print "Error: ", e," for URL: ", url.encode('ascii','ignore')
            try_count += 1
        except:
            print "Error for URL: ", url.encode('ascii','ignore')
            try_count += 1               
        else:
            break
    
    if try_count == 2:
        print "Try count exceeded."
        return False
   
    if rp.is_allowed("*", url):
        allowed = True
    else:
        allowed = False
    return allowed

'''WORLD WAR 2
	http://www.history.com/topics/world-war-ii
	http://en.wikipedia.org/wiki/World_War_II
	http://en.wikipedia.org/wiki/List_of_World_War_II_battles_involving_the_United_States
	http://en.wikipedia.org/wiki/Military_history_of_the_United_States_during_World_War_II'''

'''an id, the URL, the HTTP headers, the page contents cleaned (with term positions), the raw html, and a list of all
in-links (known) and out-links for the page.'''
start_time = str(datetime.now())
print "starting in time :",start_time

depth = 0
#learn_depth_limit = 2
rel_check = rc.RelevanceChecker()
c = Canonicalizer()
es = Elasticsearch()

seed_url1 = 'http://en.wikipedia.org/wiki/List_of_World_War_II_battles_involving_the_United_States'
seed_url2 = 'http://en.wikipedia.org/wiki/Military_history_of_the_United_States_during_World_War_II'
seed_url3 = 'http://en.wikipedia.org/wiki/World_War_II'
seed_url4 = 'http://www.history.com/topics/world-war-ii'
seed_url5 = 'http://www.britannica.com/EBchecked/topic/648813/World-War-II'

global banned_domains
banned_domains = ['facebook', 'amazon', 'google', 'linkedin', 'youtube', 'foursquare', 'plus.google',\
                  'instagram', 'twitter', 'email', 'flickr', 'vine', 'meetup', 'tumblr', 'videos', 'pictures', 'games', 'audio'] #ww1?

front = frontier.FrontierQueue([seed_url1, seed_url2, seed_url3, seed_url4, seed_url5])
#front = frontier.FrontierQueue([seed_url1])

count = 0
explored = {}
in_link_dict = {}
opener = urllib2.build_opener()
headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:10.0.1) Gecko/20100101 Firefox/10.0.1',
}
topic = 'world+war+2'
opener.addheaders = headers.items()
topic_response = opener.open("http://api.datamuse.com/words?rd="+topic+"&max=2000").read()
topic_seed = json.loads(topic_response)
topic_seed = [x["word"] for x in topic_seed if x['score'] > 38661]
print len(topic_seed)

st = 1
et = 0
while True:
    print "time taken ",et - st
    #being polite  
    if et - st < 1:
        time.sleep(1)

    st = time.time()    
    if front.isEmpty():
        print "QUEUE EMPTY"
        break
    else:
        url, depth, in_links = front.pop()
        
    print count, "Crawl started for URL ", url.encode('ASCII','ignore'), " in links: ", in_links
    in_link_dict[url] = in_links

    if explored.get(url) == None:
        visited = False
    else:
        #print "Url already visited.Skipping... ", url
        visited = True

    allowed = policy_rules(url)

    if allowed and not visited:
        
        redo_count = 0
        while redo_count < 2:
            try: response = opener.open(url)
            except urllib2.URLError as e:
                print "Error: ", e," for URL: ", url.encode('ascii','ignore')
                redo_count += 1
            except:
                print "Error for URL: ", url.encode('ascii','ignore')
                redo_count += 1               
            else:
                break
        
        if redo_count == 2:
            print "redo count exceeded. Skipping..."
            continue

        html = response.read()
        header = json.dumps(response.info().dict)
        try: header_info = response.info().dict['content-type']
        except KeyError as e:
            print "KeyError ",e," Skipping..."
            continue
        except:
            print "Error, skipping..."
            continue
        
        if len(re.findall('text/html',header_info)) == 0:
            print "Link not text/html.Skipping..."
            continue

        soup = BeautifulSoup(html)

        if soup.title == None:
            title = ""
        else:
            if soup.title.string == None:
                title = ""
            else:
                title = soup.title.string.encode('ascii','ignore')
        title = title.replace("\n"," ")
        text_list = [''.join(s.findAll(text=True)) for s in soup.find_all('p')]
        body_text = '.'.join(text_list).encode('ascii','ignore')
        if soup.find("table") == None:
            table_text = ''
        else:
            table_text = soup.find("table").get_text().encode('ascii','ignore')

        text = body_text + table_text
        text = text.replace("\n",' ')
        
        relevance = rel_check.is_relevant(text, title, topic_seed)
        if relevance:
            #rel_check.update_topic_scores(url)
            pass
        else:
            print "Offtopic url, skipping..."
            #rel_check.penalise_scores(url)
            doc = {'url': url}
            with open("off_topic_log.txt","a+") as fot:
                fot.write(json.dumps(doc)+"\n")
            continue
         

        links = []

        for link in soup.find_all('a'):
            link_ref = link.get('href')
            if link_ref is not None  and link_ref != '' and link_ref[0]!='#':
                if len(link.contents) != 0 and isinstance(link.contents[0], element.NavigableString):
                    anchor_text = str(link.contents[0].encode('ascii','ignore'))    # fetch anchor text                    
                    #print "anchor text for link: ",link.get('href'), " is ",anchor_text.encode('ascii','ignore')
                else:
                    continue
                # rank mechanism so that less relevant topics are trimmed off after count = 10 or 100 
                '''if depth < learn_depth_limit:
                    word_list = rel_check.extract_relevant_words(anchor_text.lower())
                    for domain in banned_domains:
                        if domain in word_list:
                            word_list = [x for x in word_list if x != domain]
                        else:
                            word_list = [x for x in word_list if len(x) > 1]
                    rel_check.update_topic(word_list)'''
                    
                #else:
                if rel_check.is_valid_anchor(anchor_text, topic_seed):
                    pass
                else:
                    #print "Offtopic, skipping..."
                    doc = {'url': link.get('href'), 'anchor_text': anchor_text}
                    with open("off_topic_log.txt","a+") as fot:
                        fot.write(json.dumps(doc)+"\n")
                    continue
                
                links.append(link.get('href'))

        #links = links[:2]
	if explored.get(url) == None:
                explored[url] = set()
        for out_url in links:
            # Before canonicalization
            new_url = c.canonicalize(out_url, url)
            # After canonicalization
            if front.exists(new_url):
                #print "Url exists in front (main)"
                front.update(new_url, url)
            elif explored.get(new_url) != None:
                #print "Url doesn't exist in front (main) but exists in explored"
                in_link_dict[new_url].add(url)
                #if is_present(es, docNo):
                existing_in_links = es.get(index = 'vs_dataset', doc_type = 'document', id = 3, fields = ['in_links'])
                new_in_links = existing_in_links.append(url)
                res = es.update(index = 'vs_dataset', doc_type = 'document', id = new_url, body = {u'in_links': {"script": 'update_links'}})
            else:
                #print "Url doesn't exist in front and doesn't exists in explored (new)"
                front.push(new_url, depth + 1, url)
            explored[url].add(new_url)

        docNo = url.encode('ascii','ignore')
        docLength = len(text)

        with open("output/"+"VS_"+str(count)+".txt",'w') as f:
            f.write("<DOC>\n")
            f.write("<DOCNO>" + docNo + "</DOCNO>\n")
            f.write("<TITLE>" + title + "</TITLE>\n")
            f.write("<TEXT>\n")
            f.write(text + "\n")
            f.write("</TEXT>\n")
            f.write("<IN_LINKS>\n")
            f.write(str(in_link_dict[url]) + "\n")
            f.write("</IN_LINKS>\n")
            f.write("<OUT_LINKS>\n")
            f.write(str(explored[url]) + "\n")
            f.write("</OUT_LINKS>\n")
            f.write("<HEADER>\n")
            f.write(str(header) + "\n")
            f.write("</HEADER>\n")
            f.write("<HTML>\n")
            f.write(str(html) + "\n")
            f.write("</HTML>\n")
            f.write("</DOC>")


        doc = {
                'docno': docNo,
                'title': title,
                'text': text,
                'in_links': in_link_dict[url],
                'out_links': explored[url],
                'header': header,
                'raw_html': html,
                'docLength': docLength
                }
        res = es.index(index="vs_dataset", doc_type='document', id = docNo, body = doc)

        #print "write successful for url", url
        
        #TODO update_link_graph(url, links)
        #TODO Edit distance graph for similar pages

        count += 1
        #if count % 20 == 0:
            #rel_check.update_banned_domains()
        if count % 10 == 0:

            with open("logs/topic_" + str(count) + ".log","w") as flog:
                flog.write(str(topic_seed))
            front.write_logs(count)
            with open("logs/in_link_" + str(count) + ".log","w") as flog:
                flog.write(str(in_link_dict))
            with open("logs/out_link_" + str(count) + ".log","w") as flog:
                flog.write(str(explored))

            print "There are ", len(in_link_dict)," in_link_dict\n"
            print "There are ", len(explored)," explored\n"


        if count == 20:#70000:
            break
    else:
        print "Skipping URL: ", url.encode('ascii','ignore'), "Allowed : ", allowed, "Visited: ",visited
    et = time.time()
    #print count," Crawl for URL complete ", url
    #print "\n\n"
end_time = str(datetime.now())
et = time.time()
print "start time is ",start_time," and end time is ",end_time
print "time taken ",et - st
