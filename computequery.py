from elasticsearch import Elasticsearch
from elasticsearch import client
import string

def find_average_doc_length(maxSize):    
    avgDoclengthResult = es.search(index="ap_dataset", doc_type="document", 
        body = { "aggs":{"avg_doc_length":{"avg":{"script":"doc['doclength'].values"}}}})
    avgDocLength = avgDoclengthResult['aggregations']['avg_doc_length']['value']
    return avgDocLength

def find_sum_doc_length(maxSize):    
    sumDoclengthResult = es.search(index="ap_dataset", doc_type="document", 
        body = { "aggs":{"sum_doc_length":{"sum":{"script":"doc['doclength'].values"}}}})
    sumDocLength = sumDoclengthResult['aggregations']['sum_doc_length']['value']
    return sumDocLength


def calc_okapitf(query, queryNo, avgDocLength):
    fOkaptiTf = open("Results/okapi_tf_output.txt",'a')
    queryArray = []
    ic = client.IndicesClient(es)
    analyzedResult = ic.analyze(index="ap_dataset",analyzer="my_english",body=query)
    tokenLength = len(analyzedResult['tokens'])
    for i in range(tokenLength):
        queryArray.append(str(analyzedResult['tokens'][i]['token']))
    
    queryBody = {"query": {"function_score": {"query": {"match": {"text": query}},
        "functions":[{"script_score": {"script": "getOkapiTF", "lang": "groovy", 
            "params": {"query": queryArray, "field":"text", "avgLength": avgDocLength}}}], 
        "boost_mode": "replace"}}, "fields":["stream_id"]}
    okapiResult = es.search(index="ap_dataset", doc_type="document", size = 100, 
        analyzer = "my_english", body = queryBody)
    
    resultSize = len(okapiResult['hits']['hits'] )
    rank = 1
    for i in range(resultSize):
        docId = str(okapiResult['hits']['hits'][i]['_id'])
        score = okapiResult['hits']['hits'][i]['_score']
        if score != 0:
            fOkaptiTf.write(queryNo + " Q0 " + docId + " " + str(rank) + " " + str(score) + " Exp\n")
            rank = rank + 1
    fOkaptiTf.close()

def calc_tf_idf(query, queryNo, avgDocLength, nDocs):
    fTtIdf = open("Results/tf_idf_output.txt",'a')
    queryArray = []
    ic = client.IndicesClient(es)
    analyzedResult = ic.analyze(index="ap_dataset",analyzer="my_english",body=query)
    tokenLength = len(analyzedResult['tokens'])
    for i in range(tokenLength):
        queryArray.append(str(analyzedResult['tokens'][i]['token']))
    
    queryBody = {"query": {"function_score": {"query": {"match": {"text": query}},
        "functions":[{"script_score": {"script": "getTfIdf", "lang": "groovy", 
            "params": {"query": queryArray, "field":"text", "avgLength": avgDocLength, "ndocs" : nDocs}}}],
        "boost_mode": "replace"}}, "fields":["stream_id"]}
    tfIdfResult = es.search(index="ap_dataset", doc_type="document", size = 100, 
        analyzer = "my_english", body = queryBody)
    
    resultSize = len(tfIdfResult['hits']['hits'] )
    rank = 1
    for i in range(resultSize):
                
        docId = str(tfIdfResult['hits']['hits'][i]['_id'])
        score = tfIdfResult['hits']['hits'][i]['_score']
        if score != 0:
            fTtIdf.write(queryNo + " Q0 " + docId + " " + str(rank) + " " + str(score) + " Exp\n")
            rank = rank + 1
    
    fTtIdf.close()

def calc_okapi_BM(query, queryNo, avgDocLength, nDocs):
    fokapiBM = open("Results/okapiBM_output.txt",'a')
    queryArray = []
    ic = client.IndicesClient(es)
    analyzedResult = ic.analyze(index="ap_dataset",analyzer="my_english",body=query)
    tokenLength = len(analyzedResult['tokens'])
    for i in range(tokenLength):
        queryArray.append(str(analyzedResult['tokens'][i]['token']))
    
    queryBody = {"query": {"function_score": {"query": {"match": {"text": query}},
        "functions":[{"script_score": {"script": "getOkapiBM", "lang": "groovy", 
            "params": {"query": queryArray, "field":"text", "avgLength": avgDocLength, "ndocs" : nDocs}}}],
        "boost_mode": "replace"}}, "fields":["stream_id"]}
    okapiBMResult = es.search(index="ap_dataset", doc_type="document", size = 100, 
        analyzer = "my_english", body = queryBody)
    
    resultSize = len(okapiBMResult['hits']['hits'] )
    rank = 1
    for i in range(resultSize):
                
        docId = str(okapiBMResult['hits']['hits'][i]['_id'])
        score = okapiBMResult['hits']['hits'][i]['_score']
        if score != 0:
            fokapiBM.write(queryNo + " Q0 " + docId + " " + str(rank) + " " + str(score) + " Exp\n")
            rank = rank + 1
    fokapiBM.close()

def calc_laplace(query, queryNo, vocabSize):
    flaplace = open("Results/laplace_output.txt",'a')
    queryArray = []
    ic = client.IndicesClient(es)
    analyzedResult = ic.analyze(index="ap_dataset",analyzer="my_english",body=query)
    tokenLength = len(analyzedResult['tokens'])
    for i in range(tokenLength):
        queryArray.append(str(analyzedResult['tokens'][i]['token']))
    
    queryBody = {"query": {"function_score": {"query": {"match": {"text": query}},
        "functions":[{"script_score": {"script": "getLaplace", "lang": "groovy", 
            "params": {"query": queryArray, "field":"text", "vocabSize": vocabSize}}}], 
        "boost_mode": "replace"}}, "fields":["stream_id"]}
    laplaceResult = es.search(index="ap_dataset", doc_type="document", size = 100, 
        analyzer = "my_english", body = queryBody)
    
    resultSize = len(laplaceResult['hits']['hits'] )
    rank = 1
    for i in range(resultSize):
                
        docId = str(laplaceResult['hits']['hits'][i]['_id'])
        score = laplaceResult['hits']['hits'][i]['_score']
        if score != 0:
            flaplace.write(queryNo + " Q0 " + docId + " " + str(rank) + " " + str(score) + " Exp\n")
            rank = rank + 1
    
    flaplace.close()

def calc_JM(query, queryNo, lamb, sumDocLength):
    fjm = open("Results/jm_output.txt",'a')
    queryArray = []
    ic = client.IndicesClient(es)
    analyzedResult = ic.analyze(index="ap_dataset",analyzer="my_english",body=query)
    tokenLength = len(analyzedResult['tokens'])
    for i in range(tokenLength):
        queryArray.append(str(analyzedResult['tokens'][i]['token']))
    
    queryBody = {"query": {"function_score": {"query": {"match": {"text": query}},"functions":[{"script_score": {"script": "getJM", "lang": "groovy", "params": {"query": queryArray, "field":"text", "lamb": lamb, "sumdoclength": sumDocLength }}}], "boost_mode": "replace"}}, "fields":["stream_id"]}
    jmResult = es.search(index="ap_dataset", doc_type="document", size = 100, analyzer = "my_english", body = queryBody)
    
    resultSize = len(jmResult['hits']['hits'] )
    rank = 1
    for i in range(resultSize):
                
        docId = str(jmResult['hits']['hits'][i]['_id'])
        score = jmResult['hits']['hits'][i]['_score']
        if score != 0:
            fjm.write(queryNo + " Q0 " + docId + " " + str(rank) + " " + str(score) + " Exp\n")
            rank = rank + 1
    
    fjm.close()
    
es = Elasticsearch(timeout = 180)

filepath = 'Query Processor/AP89_DATA/AP_DATA/'
queryFilename = 'query_desc.51-100.short.txt'

fquery = open(filepath+"/"+queryFilename)
queryData = fquery.readlines()

stopFilePath = "elasticsearch-1.4.2/elasticsearch-1.4.2/config"
stopFileName = 'stoplist.txt'
fstop = open(stopFilePath+"/"+stopFileName)
stopFileData = fstop.readlines()
stopFileData = [x.replace("\n",'') for x in stopFileData]

queryCount = 1
# calculated using Sense
maxSize = 84678
vocabSize = 140292
lamb = 0.5

print "\nCalculating average Document Lengths..."
avgDocLength = find_average_doc_length(maxSize)
print "\naverage doc Length is ", avgDocLength

print "\nCalculating sum Document Lengths..."
sumDocLength = find_sum_doc_length(maxSize)
print "\nSum doc Length is ", sumDocLength

for line in queryData:
    
    lineArray = line.split(".")
    queryNo = lineArray[0]
    query = lineArray[1]
    
    # Removing Ignored words from query
    query = query.replace(" Document will discuss ","")
    query = query.replace(" Document will report ","")
    query = query.replace(" Document will include ","")
    query = query.replace(" Document must describe ","")
    query = query.replace(" Document must identify ","")
    
    # Removing punctuations from query
    for p in string.punctuation:
        if p != '_' and p!='-':
            query = query.replace(p," ")
    
    tlist = query.split()
    slist=[]
    for i in range(len(tlist)):
        if tlist[i] in stopFileData:
            slist.append('')
        else:
            slist.append(tlist[i])
    query = ' '.join(slist)
    
    # Removing double spaces from query
    query = query.replace("  "," ")
    # Converting to lowertext
    query = query.lower()

    print "Running Query no: ",queryNo," query count",queryCount
    queryCount += 1

    print "Fetched results for Query no: ",queryNo

    '''
    #Using built-in score
    for i in range(maxNum):
        docId = str(res['hits']['hits'][i]['_id'])
        rank = str(i)
        score = str(res['hits']['hits'][i]['_score'])
        #<query-number> Q0 <docno> <rank> <score> Exp
        if score!= 0:
            fw.write(queryNo+" Q0 "+docId+" "+rank+" "+score+" Exp\n")
    '''
    
    calc_okapitf(query, queryNo, avgDocLength)
    calc_tf_idf(query, queryNo, avgDocLength, maxSize)
    calc_okapi_BM(query, queryNo, avgDocLength, maxSize)
    calc_laplace(query, queryNo, vocabSize)
    calc_JM(query, queryNo, lamb, sumDocLength)
    
fquery.close()    
fstop.close()



