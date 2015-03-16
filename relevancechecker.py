__author__ = 'Abhijeet Sharma'

import re
import string

class RelevanceChecker:
    '''Relevance check in text and anchor links'''    

    def  __init__(self):
        self.topic_set = set(["world","war", "battle"])
        stopFileName = 'stoplist.txt'
        with open(stopFileName,'r') as fstop:
            self.stopFileData = fstop.readlines()
        self.stopFileData = [x.replace("\n",'') for x in self.stopFileData]
        
    def is_relevant(self, text, head):
        count = 0
        for topic in self.topic_set:
            topic_check = re.compile(topic,re.IGNORECASE)
            text_check = topic_check.search(text)
            head_check = topic_check.search(head)
            if text_check == None and head_check == None:
                continue
            else:
                count += 1
        
        if count >= 2:
            return True
        else:
            return False
    
    def is_valid_anchor(self, anchor_text, link_ref):
        count = 0
        for topic in self.topic_set:
            topic_check = re.compile(topic,re.IGNORECASE)
            text_check = topic_check.search(anchor_text)
            link_check = topic_check.search(link_ref)
            if text_check == None and link_check == None:
                continue
            else:
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
        self.topic_set.update(word_list)

    
    def fetch_set(self):
        return self.topic_set