__author__ = 'abhijeet'

from elasticsearch import Elasticsearch
from elasticsearch import client
from relevancechecker import RelevanceChecker
#import string


class Computequery(object):
    """computes the result based on user input query"""

    def __init__(self):
        #self.es = Elasticsearch(hosts=[{'host': '10.0.0.9', 'port': 9200}], timeout=180)
        self.es = Elasticsearch(hosts=[{'host': '192.168.43.85', 'port': 9200}], timeout=180)
        self.rc = RelevanceChecker()
        # calculated using Sense
        # self.maxSize = 84678
        # self.vocabSize = 140292
        # self.lamb = 0.5

    def fetch_results(self, query, query_size):
        # query = self.rc.remove_stop(query)
        ic = client.IndicesClient(self.es)

        print "Running Query ", query


        # Querying using built-in score
        query_array = []
        analyzed_result = ic.analyze(index="vs_dataset",analyzer="my_english",body=query)
        token_length = len(analyzed_result['tokens'])
        for i in range(token_length):
            query_array.append(str(analyzed_result['tokens'][i]['token']))

        query = ' '.join(query_array)
        query_body = {"query": {"multi_match": {"query": query, "fields": ["title","text"]}}}

        res = self.es.search(index="vs_dataset", doc_type="document", size=query_size, analyzer="my_english", body=query_body)
        time_taken = res['took']
        results_num = len(res['hits']['hits'])
        print "time taken", time_taken
        results = dict()

        for i in range(results_num):
            doc_id = str(res['hits']['hits'][i]['_id'])
            rank = i+1
            score = str(res['hits']['hits'][i]['_score'])

            source = res['hits']['hits'][i]['_source']

            title = source['title']
            text = source['text']
            in_links = source['in_links']
            out_links = source['out_links']
            header = source['header']
            raw_html = source['raw_html']
            # doc_length = source['docLength']

            if score != 0:
                results[rank] = {'docno': doc_id, 'title': title, 'text': text, 'in_links': in_links,\
                                'out_links': out_links, 'header': header, 'raw_html': raw_html, \
                                'score': score}

                '''print doc_id
                print rank
                print score
                print title
                print in_links
                print out_links
                print "\n"'''
            print doc_id
        print "score computation complete ", len(results)
        return results, time_taken, results_num