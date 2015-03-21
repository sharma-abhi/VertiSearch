__author__ = 'Abhijeet Sharma'

import re
import string


class RelevanceChecker:
    """Relevance check in title, body text and anchor texts"""

    def __init__(self):

        stop_file_name = 'stoplist.txt'
        with open(stop_file_name,'r') as fstop:
            self.stop_data = fstop.readlines()
        self.stop_data = [x.replace("\n",'') for x in self.stop_data]

    # This function checks for relevance in body and title of website
    @staticmethod
    def is_relevant(text, title, topic_seed):
        count = 0
        for topic in topic_seed:
            topic_check = re.compile(r'\b' + topic + r'\b',re.IGNORECASE)
            text_check = topic_check.search(text)
            title_check = topic_check.search(title)
            if text_check is None and title_check is None:
                continue
            else:
                count += 1
        
        if count >= 1:
            return True
        else:
            return False

    # This function checks for relevance in anchor text.
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
        # removing punctuations
        for p in string.punctuation:
            if p != '_' and p!='-':
                input_string = input_string.replace(p," ")
        tlist = input_string.split()

        # removing stop words
        slist = list()
        for i in range(len(tlist)):
            if tlist[i] in self.stop_data:
                slist.append('')
            else:
                slist.append(tlist[i])
        input_string = ' '.join(slist)

        # removing end-of-line characters
        input_string = input_string.replace("\n","")

        # removing double spaces
        input_string = input_string.replace("  "," ")

        # converting all text to lower
        input_string = input_string.lower()

        return input_string


