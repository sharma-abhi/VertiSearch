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
from canonicalization import Canonicalizer as canon
from elasticsearch import Elasticsearch
from elasticsearch import exceptions


# This function checks whether the given docNo is present in ElasticSearch or not.
# INPUT: docNo, which is the unique identifier for a document in ElasticSearch.
# OUTPUT: True if the particular document is present, False otherwise.
def is_present(elastic, doc_no):
    try:
        req = elastic.get(index='vs_dataset', doc_type='document', id=doc_no, fields=['text'])
    except exceptions.NotFoundError as err:
        log_error(err, doc_no)
        return False
    except:
        return False
    else:
        return True


# This function extracts the hostname from any url.
# INPUT: a url for a website.
# OUTPUT: the host url for the given url.
def host_extract(full_url):
    # extract host url
    parsed_url = up.urlparse(full_url)
    host_scheme = parsed_url[0]
    host_url = parsed_url[1]
    new_parsed_url = (host_scheme, host_url, "", "", "", "")
    return up.urlunparse(new_parsed_url)


# This function checks the site's robots.txt for crawling permission.
# INPUT: a url for a website
# OUTPUT: whether the crawler is allowed to crawl the website or not.
def policy_rules(full_url, limit):
    # list of banned domains
    banned_domains = ['facebook', 'amazon', 'google', 'linkedin', 'youtube', 'foursquare', 'plus.google', \
                      'instagram', 'twitter', 'email', 'flickr', 'vine', 'meetup', 'tumblr', 'videos', \
                      'pictures', 'games', 'audio']
    
    host_url = host_extract(full_url)
   
    # excluding sites like Facebook, Amazon, Linkedin, etc.
    for domain in banned_domains:
        if domain in host_url:
            print "Banned Domain", domain ," Skipping..."
            return False

    rp = rerp.RobotExclusionRulesParser()
    try_count = 0
    while try_count < limit:
        try: rp.fetch(host_url+'/robots.txt')
        except urllib2.URLError as err:
            print "Error: ", err," for URL: ", url.encode('ascii', 'ignore')
            try_count += 1
            log_error(err, url)
        except UnicodeError as err:
            print "Error: ", err, " for URL: ", url.encode('ascii', 'ignore')
            try_count += 1
            log_error(err, url)
        else:
            # retry limit reached, skip this url.
            break

    # retry for fetching url failed
    if try_count == 2:
        print "Try count exceeded."
        return False

    # check for permission
    if rp.is_allowed("*", url):
        return True
    else:
        return False


# This function logs all the runtime errors
def log_error(error, error_reason):
    error_reason = error_reason.encode(encoding_format, 'ignore')
    with open("run_errors.log","a+") as ferr:
        ferr.write("Error detected: " + str(error) + "for url: " + str(error_reason) + "\n")

def save_to_file(json_object, file_obj):
    file_obj.write("<DOC>\n")

    file_obj.write("<DOCNO>" + str(json_object.get('docno')) + "</DOCNO>\n")

    file_obj.write("<TITLE>" + str(json_object.get('title')) + "</TITLE>\n")

    file_obj.write("<INLINK>" + str(json_object.get('in_links')) + "</INLINK>\n")

    file_obj.write("<OUTLINK>" + str(json_object.get('out_links')) + "</OUTLINK>\n")

    file_obj.write("<HEADER>" + str(json_object.get('header')) + "</HEADER>\n")

    file_obj.write("<TEXT>\n")
    file_obj.write(str(json_object.get('text')))
    file_obj.write("\n</TEXT>\n")

    file_obj.write("<CONTENT>\n")
    file_obj.write(json_object.get('raw_html'))
    file_obj.write("\n</CONTENT>\n")

    file_obj.write("<DOCLEN>" + str(json_object.get('doclength')) + "</DOCLEN>\n")

    file_obj.write("</DOC>\n")

############################### start of program ###########################
# TODO: make command line arguments for topic generalization
topic = 'world+war+2'
encoding_format = 'ascii'
cutoff_limit = 70000
logging_limit = 1000

# Timekeeping
start_time = str(datetime.now())
start_ts = time.time()
st = 0  # start time
et = 1  # end time
print "starting in time :", start_time

# Initialization of seeds
# TODO: Read from a file for generalization
seed_url1 = 'http://en.wikipedia.org/wiki/List_of_World_War_II_battles_involving_the_United_States'
seed_url2 = 'http://en.wikipedia.org/wiki/Military_history_of_the_United_States_during_World_War_II'
seed_url3 = 'http://en.wikipedia.org/wiki/World_War_II'

# Inserting seed url
front = frontier.FrontierQueue([seed_url1, seed_url2, seed_url3])

rel_check = rc.RelevanceChecker()
es = Elasticsearch(hosts=[{'host': '10.0.0.9', 'port': 9200}], timeout=180)

# no. of retry attempts for fetching data from a website
retry_limit = 2

# Initializing counter for logging and cutoff process.
count = 0

# initializing dictionary for holding in links
in_link_dict = {}

# initializing dictionary for holding out links
explored = {}

# The minimum score for fetching relevant topics
topic_score_limit = 38661

# fetching relevant topic keywords (topic seeds)
opener = urllib2.build_opener()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:10.0.1) Gecko/20100101 Firefox/10.0.1'}
opener.addheaders = headers.items()
topic_response = opener.open("http://api.datamuse.com/words?rd="+topic+"&max=2000").read()
topic_seed = json.loads(topic_response)

# filter only the high score topics
topic_seed = [x["word"] for x in topic_seed if x['score'] > topic_score_limit]
print "Length of seed list for topic : ", topic," is :", len(topic_seed)


while not front.is_front_empty():
    # initializing links
    links = []

    time_diff = et - st
    print "time taken ", time_diff

    # being polite...only if time taken by previous compute is less than 1 second.
    if time_diff < 1:
        time.sleep(1)
    st = time.time()

    # Pop an url and it's corresponding in-links
    url, in_links = front.pop()
    in_link_dict[url] = in_links
    print count, "Crawl started for URL ", url.encode(encoding_format,'ignore'), " in links: ", in_links

    # If this website has already been crawled, no need to crawl again
    # Can implement an update fn.for updating modified websites (for version 2.0).
    if explored.get(url) is None:
        visited = False
        # initialize explored set for fresh url.
        explored[url] = set()
    else:
        visited = True

    # fetch robot policy rules
    allowed = policy_rules(url, retry_limit)

    if allowed and not visited:
        redo_count = 0
        while redo_count < retry_limit:
            try:
                response = opener.open(url)
            except urllib2.URLError as e:
                print "Error: ", e," for URL: ", url.encode(encoding_format, 'ignore')
                log_error(e, url)
                redo_count += 1
            else:
                # retry limit reached, skip this url.
                break
        
        if redo_count == retry_limit:
            # skip this url.
            print "redo count exceeded. Skipping..."
            continue

        # fetch data from url
        html = response.read()

        # fetch HTTP header
        header = json.dumps(response.info().dict)

        # fetch 'content-type' data from website's header data.
        try:
            header_info = response.info().dict['content-type']
        except KeyError as e:
            # there is no 'content-type' field.skip url.
            print "KeyError ", e," Skipping..."
            log_error(e, url)
            continue

        # if header is not html, skip
        if len(re.findall('text/html',header_info)) == 0:
            print "Link not text/html.Skipping..."
            continue

        # make it beautiful.
        soup = BeautifulSoup(html)

        # fetching title for the website.If there is no title, insert blank.
        if soup.title is None:
            title = ""
        else:
            if soup.title.string is None:
                title = ""
            else:
                title = soup.title.string.encode(encoding_format,'ignore')

        # cleaning title
        title = title.replace("\n"," ")

        # fetching text from the website
        text_list = [''.join(s.findAll(text=True)) for s in soup.find_all('p')]
        body_text = '.'.join(text_list).encode(encoding_format, 'ignore')

        # if there is table,fetch table text
        if soup.find("table") is None:
            table_text = ''
        else:
            table_text = soup.find("table").get_text().encode(encoding_format, 'ignore')

        # combine both body text and table text
        text = body_text + table_text
        text = text.replace("\n",' ')

        # checking whether website is relevant or not.
        relevance = rel_check.is_relevant(text, title, topic_seed)
        if relevance:
            # do nothing
            pass
        else:
            # log off topics and skip website.
            print "Offtopic url, skipping..."
            off_topic = {'url': url}
            with open("off_topic_log.txt","a+") as fot:
                fot.write(json.dumps(off_topic)+"\n")
            continue

        # extracting out links
        for link in soup.find_all('a'):

            # fetch out link
            link_ref = link.get('href')
            anchor_text = ""
            # check if link is valid or not.
            if link_ref is not None  and link_ref != '' and link_ref[0] != '#':
                # check if link has valid anchor text
                if len(link.contents) != 0 and isinstance(link.contents[0], element.NavigableString):
                    # fetching anchor text to identify relevancy.
                    anchor_text = str(link.contents[0].encode(encoding_format, 'ignore'))
                else:
                    # if link doesn't have valid anchor text, skip link.
                    continue

                # checking anchor text for relevancy.
                if rel_check.is_valid_anchor(anchor_text, topic_seed):
                    # if valid anchor text found, do nothing
                    pass
                else:
                    # if anchor text is offtopic, skip link.
                    doc = {'url': link.get('href'), 'anchor_text': anchor_text}
                    with open("off_topic_log.txt","a+") as fot:
                        fot.write(json.dumps(doc)+"\n")
                    continue

                # if link is good, add it to list
                links.append(link.get('href'))

        # processing each valid out links
        for out_link in links:

            # Canonicalization of out link.
            canonical_out_link = canon.canonicalize(out_link, url)
            # if after canonicalization, we get same url, skip.
            if canonical_out_link == url:
                log_error("skipped becase url produced same canonicalization out-link as itself: ", out_link)
                continue

            # check if link(url) exists in the frontier set.
            if front.exists(canonical_out_link):
                # update the out-link's in-link dictionary with current crawled url.
                front.update(canonical_out_link, url)

            # check if link(url) doesn't exist in the frontier set but exists in the explored set.
            elif explored.get(canonical_out_link) is not None:

                # update elastic search with the new in link.
                es_body = {u'in_links': {"script": 'update_links', "params": {"new_link": url}}}
                try:
                    res = es.update(index='vs_dataset', doc_type='document', id=canonical_out_link, body=es_body)
                    with open("output/updates.txt","a+") as fw:
                        fw.write(str({canonical_out_link: url}) + "\n")
                except exceptions.NotFoundError as err:
                    log_error(err, canonical_out_link)
                    continue
                except exceptions.ConnectionError as err:
                    log_error(err, canonical_out_link)
                    continue
                except:
                    log_error("Other Errors", canonical_out_link)
                    continue
            # check if link(url) doesn't exist in the frontier set and doesn't exists in the explored set also.
            else:
                front.push(canonical_out_link, url)

            # add link to explored set as an out link.
            explored[url].add(canonical_out_link)

        # cleaning url for insertion to ElasticSearch.
        docNo = url.encode(encoding_format,'ignore')

        # cleaning text for insertion to ElasticSearch.
        # text = rel_check.remove_stop(text)

        # calculating docLength for insertion to ElasticSearch.
        # docLength = len(text.split())
        doc = {
                'docno': docNo,
                'title': title,
                'text': text,
                'in_links': list(in_link_dict[url]),
                'out_links': list(explored[url]),
                'header': str(header),
                'raw_html': str(html.decode(encoding_format, 'ignore')),
                }

        # indexing document in Elastic Search
        try:
            res = es.index(index="vs_dataset", doc_type='document', id=docNo, body=doc)
        except:
            log_error("index already present", url)
            print "Index UnSuccessful for url", url
        else:
            with open("output/vs_" + str(count) + ".txt","w") as fw:
                save_to_file(doc, fw)
            print "Index successful for url", url

        # incrementing counter
        count += 1

        # logging data
        if count % logging_limit == 0:
            # logging topic seeds
            with open("logs/topic_" + str(count) + ".log","w") as flog:
                flog.write(str(topic_seed))
            # logging frontier data
            front.write_logs(count)

        # check for cutoff limit.If limit reached, stop crawler.
        if count == cutoff_limit:
            print "Cutoff limit reached.Congratulations."
            break
    else:
        # Url either not allowed to crawl or already visited.Skip url.
        print "Skipping URL: ", url.encode(encoding_format, 'ignore'), "Allowed: ", allowed, "Visited: ", visited
    et = time.time()

# output for program execution time.
end_time = str(datetime.now())
end_ts = time.time()
print "start time is: ", start_time," and end time is: ", end_time
print "time taken: ", end_ts - start_ts
# TODO main()
# TODO update_link_graph(url, links)
# TODO Edit distance graph for similar pages
