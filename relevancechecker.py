__author__ = 'Abhijeet Sharma'

import re
import string

class RelevanceChecker:
    '''Relevance check in text and anchor links'''    

    def  __init__(self):
        self.topic_seed = set(["world","war", "battle"])
        self.topic_set = set(["world","war", "battle"])
        stopFileName = 'stoplist.txt'
        with open(stopFileName,'r') as fstop:
            self.stopFileData = fstop.readlines()
        self.stopFileData = [x.replace("\n",'') for x in self.stopFileData]
        self.topics = {}
        self.score = {"world":10000000000000000, "war":10000000000000000, "battle":10000000000000000}
        
    def is_relevant(self, text, title):
        count = 0
        for topic in self.topic_seed:
            topic_check = re.compile(r'\b' + topic + r'\b',re.IGNORECASE)
            text_check = topic_check.search(text)
            title_check = topic_check.search(title)
            if text_check == None and title_check == None:
                continue
            else:
                count += 1
        
        if count >= 2:
            return True
        else:
            return False
    
    def is_valid_anchor(self, anchor_text, link_ref, new_link_ref):
        count = 0
        for topic in self.topic_set:
            topic_check = re.compile(topic,re.IGNORECASE)
            text_check = topic_check.search(anchor_text)
            link_check = topic_check.search(link_ref)
            if text_check == None and link_check == None:
                continue
            else:
                if self.topics.get(new_link_ref) == None:
                    self.topics[new_link_ref] = set([topic])
                else:
                    self.topics[new_link_ref].add(topic)
                count += 1
        
        if count >= 1:
            return True
        else:
            return False
            
    def extract_relevant_words(self, anchor_text):
        anchor_text = anchor_text.encode('ascii','ignore')
        anchor_text = self.after_remove_stop(anchor_text)
        anchor_list = anchor_text.split()
        return anchor_list
        
    def after_remove_stop(self, input_string):
        # Removing punctuations from query
        for p in string.punctuation:
            if p != '_' and p!='-':
                input_string = input_string.replace(p," ")
    
        # removing stop words
        tlist = input_string.split()
        slist=[]
        for i in range(len(tlist)):
            if tlist[i] in self.stopFileData:
                slist.append('')
            else:
                slist.append(tlist[i])
        input_string = ' '.join(slist)
    
        input_string = input_string.replace("\n","")
        # Removing double spaces from query
        input_string = input_string.replace("  "," ")
        input_string = input_string.lower()
        
        return input_string
     
    def update_topic(self, word_list):
        for x in word_list:
            if self.score.get(x) == None:
            	self.score[x] = 0
        self.topic_set.update(word_list)

    
    def fetch_set(self):
        return self.topic_set
    
    def update_topic_scores(self, url):
        if self.topics.get(url) != None:
            top = self.topics[url]
            for x in top:
                self.score[x] += 1
    
    def penalise_scores(self, url):
        if self.topics.get(url) != None:
            top = self.topics[url]
            for x in top:
                self.score[x] -= 1    
                
    def remove_topics(self):
        sorted_topics = sorted(self.score, key = self.score.get, reverse = True)
        #deleted_topics = sorted_topics[2*(len(sorted_topics)/3):]
        #deleted_topics = sorted_topics[-100:]
        deleted_topics = [x for x in sorted_topics if self.score[x] > 1]
        with open("logs/deleted_topics.log","a+") as fdel:
            fdel.write(str(deleted_topics))
        for i in deleted_topics:
            if i in self.topic_set:
                self.topic_set.remove(i)
            
            
    def fetch_scores(self):
        return self.score

    def update_topic_seed(self):
        self.topic_seed = self.topic_set
        with open("logs/current_topic_seed.log","w") as flog:
                flog.write(str(list(self.topic_seed)))