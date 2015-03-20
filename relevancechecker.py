__author__ = 'Abhijeet Sharma'

import re
import string

class RelevanceChecker:
    '''Relevance check in text and anchor links'''    

    def  __init__(self):
        #self.topic_seed = set(["world war", "ww", "ww2", "world_war", "d-day", "pearl harbor", "world war 2", "world war II", "hitler", "nazi", "schindler", "churchill", "german-occupied", "blitzkrieg", "normandy", "holocaust", "litle boy", "fat man", "thin man", "manhattan project", "hiroshima", "nagasaki", "banzai", "batle of london", "germansoviet", "eisenhower", "dunkirk", "finisterre_range_campaign"])
        #self.topic_set = set(["world","war", "battle", "world war"])
        stopFileName = 'stoplist.txt'
        with open(stopFileName,'r') as fstop:
            self.stopFileData = fstop.readlines()
        self.stopFileData = [x.replace("\n",'') for x in self.stopFileData]
        #self.topics = {}
        #self.score = {"world":10000000000000000, "war":10000000000000000, "battle":10000000000000000, "world war":10000000000000000}
        #self.score = {x: 1000000 for x in self.topic_seed}
        #self.banned_domains = set()
        #self.domain_score = {}

    # checks for relevance in body and title of website

    def is_relevant(self, text, title, topic_seed):
        count = 0
        for topic in topic_seed:
            topic_check = re.compile(r'\b' + topic + r'\b',re.IGNORECASE)
            text_check = topic_check.search(text)
            title_check = topic_check.search(title)
            if text_check == None and title_check == None:
                continue
            else:
                count += 1
        
        if count >= 1:
            return True
        else:
            return False

    #checks for relevance in anchor text
    def is_valid_anchor(self, anchor_text, topic_seed):

        count = 0
	anchor_text = self.remove_stop(anchor_text)
        anchor_list = anchor_text.split()
        for word in anchor_list:
            if word in topic_seed:
                count += 1
            else:
                continue
        if count >= 1:
            return True
        else:
            return False

    def remove_stop(self, input_string):

        for p in string.punctuation:
	    if p != '_' and p!='-':
	        input_string = input_string.replace(p," ")
	tlist = input_string.split()
	slist=[]
    	for i in range(len(tlist)):
       	    if tlist[i] in self.stopFileData:
                slist.append('')
            else:
                slist.append(tlist[i])
	input_string = ' '.join(slist)
        input_string = input_string.replace("\n","")
        input_string = input_string.replace("  "," ")
        input_string = input_string.lower()
	#return after removing stop words
        return input_string


