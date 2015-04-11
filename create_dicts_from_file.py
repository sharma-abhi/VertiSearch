__author__ = 'Abhijeet'

from os import listdir
import re
import cPickle as pickle

filepath = 'output'
filenames = listdir(filepath)
explored = {}
in_link_dict = {}
for file in filenames:
    f = open(filepath+"/"+file)
    filedata = f.readlines()
    in_link_bool = False
    in_link_string = ""
    out_link_bool = False
    out_link_string = ""
    # print file
    for line in filedata:
        if line.startswith("<DOCNO>"):
            docNo = re.search('<DOCNO>(.*)</DOCNO>' , line).group(1)
            print docNo
        elif line.startswith("<INLINK>"):
            print "inside inlink"
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
        elif line.startswith("<OUTLINK>"):
            print "inside outlink"
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
            break
    explored[docNo] = outlinks
    in_link_dict[docNo] = inlinks
    print "extraction complete for file", file
    f.close()

print len(explored.keys())
p = pickle.Pickler(open("d:/logs/explored.txt", "w"))
p.fast = True
p.dump(explored) # d is your dictionary
p.clear_memo()
p = pickle.Pickler(open("d:/logs/in_links.txt", "w"))
p.fast = True
p.dump(in_link_dict) # d is your dictionary
p.clear_memo()
