__author__ = 'Abhijeet'

from os import listdir
import re
import cPickle as pickle
from elasticsearch import Elasticsearch
from elasticsearch import exceptions
import time
from datetime import datetime

def is_present(elastic, doc_no):
    es_start_ts = time.time()
    try:
        req = elastic.get(index='vs_dataset', doc_type='document', id=doc_no, fields=['text'])
    except exceptions.NotFoundError as err:
        #log_error(err, doc_no)
        es_end_ts = time.time()
        #es_time += es_end_ts - es_start_ts
        return False
    except:
        es_end_ts = time.time()
        #es_time += es_end_ts - es_start_ts
        return False
    else:
        es_end_ts = time.time()
        #es_time += es_end_ts - es_start_ts
        return True

def update_index(doc_no, inlinks):
    es_body = {u'in_links': {"script": 'update_links', "params": {"new_link": inlinks}}}
    try:
        res = es.update(index='vs_dataset', doc_type='document', id=doc_no, body=es_body)
        with open("logs/update_index_log.log","a+") as f:
            f.write("DOCNO: " + doc_no + "\n")
            f.write("INLINK: " + inlinks + "\n")
    except exceptions.NotFoundError as err:
        print "Not Found Error", err
    except exceptions.ConnectionError as err:
        print "Connection Error", err
    except:
        print "Unknown Error"

start_time = str(datetime.now())
start_ts = time.time()
print "starting in time :", start_time

es = Elasticsearch(hosts=[{'host': 'localhost', 'port': 9200}], timeout=180)

filepath = 'output'
filenames = listdir(filepath)

for file in filenames:
    f = open(filepath+"/"+file)
    filedata = f.readlines()

    in_link_string = ""
    out_link_string = ""
    title_string = ""
    header_string = ""
    text_string = ""
    text_bool = False
    content_string = ""
    content_bool = False

    for line in filedata:
        if line.startswith("<DOCNO>"):
            doc_no = re.search('<DOCNO>(.*)</DOCNO>' , line).group(1)
            if is_present(es, doc_no):
                print "doc_no: ", doc_no, " is present"
                update_bool = True
            else:
                update_bool = False
        elif line.startswith("<INLINK>"):
            #print "inside inlink"
            in_link_string = re.search('<INLINK>(.*)</INLINK>' , line).group(1)
            in_link_string = in_link_string.replace(", u",", ")
            in_link_string = in_link_string.replace("[u","")
            in_link_string = in_link_string.replace("[","")
            in_link_string = in_link_string.replace("]","")
            in_link_string = in_link_string.replace("'","")
            in_link_string = in_link_string.replace(" ","")
            if len(in_link_string) != 0:
                in_link_list = in_link_string.split(",")
            else:
                in_link_list = []
            inlinks = [unicode(x) for x in in_link_list]
            if update_bool:
                update_index(doc_no, inlinks)
                #break
        elif line.startswith("<TITLE>"):
            title_string = re.search('<TITLE>(.*)</TITLE>', line).group(1)
        elif line.startswith("<OUTLINK>"):
            #print "inside outlink"
            out_link_string = re.search('<OUTLINK>(.*)</OUTLINK>' , line).group(1)
            out_link_string = out_link_string.replace(", u",", ")
            out_link_string = out_link_string.replace("[u","")
            out_link_string = out_link_string.replace("]","")
            out_link_string = out_link_string.replace("'","")
            out_link_string = out_link_string.replace(" ","")
            if len(out_link_string) != 0:
                out_link_list = out_link_string.split(",")
            else:
                out_link_list = []
            outlinks = [unicode(x) for x in out_link_list]
        elif line.startswith("<HEADER>"):
            header_string = re.search('<HEADER>(.*)</HEADER>', line).group(1)
        elif line.startswith("<TEXT>"):
            text_bool = True
        elif line.startswith("</TEXT>"):
            text_bool = False
        elif text_bool:
            text_string += line
        elif line.startswith("<CONTENT>"):
            content_bool = True
        elif line.startswith("</CONTENT>"):
            content_bool = False
            #if update_bool:
            #    raise Exception("Something's Wrong.Update command found but Reched Content Block.")
            doc = {
                'docno': doc_no,
                'title': title_string,
                'text': text_string,
                'in_links': list(inlinks),
                'out_links': list(outlinks),
                'header': header_string,
                'raw_html': content_string,
                }
            res = es.index(index="vs_dataset", doc_type='document', id=doc_no, body=doc)
            with open ("d:/logs/out_link_graph.txt", "a+") as f:
                tab_sep_outlinks = '\t'.join(outlinks)
                f.write(doc_no + "\t" + tab_sep_outlinks + "\n")
            with open ("d:/logs/in_link_graph.txt", "a+") as f:
                tab_sep_inlinks = '\t'.join(inlinks)
                f.write(doc_no + "\t" + tab_sep_inlinks + "\n")
            break
        elif content_bool:
            content_string += line
    print "Indexing successful for file", file
    f.close()
end_time = str(datetime.now())
end_ts = time.time()
print "start time is: ", start_time," and end time is: ", end_time
print "time taken: ", end_ts - start_ts