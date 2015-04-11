__author__ = 'Abhijeet Sharma'

import heapq
import cPickle as pickle

class FrontierQueue(object):
    """
      Implements a priority queue data structure. Each inserted item
      has a priority associated with it and the client is usually interested
      in quick retrieval of the lowest-priority item in the queue. This
      data structure allows O(1) access to the lowest-priority item.

      Seed URLs should always be crawled first.
      Prefer pages with higher in-link counts.
      If multiple pages have maximal in-link counts, choose the option which has been in the
      queue the longest"""

    def __init__(self, seed_list, is_continue, loop_cnt):

        if not is_continue:
            self.heap = []
            self.count = 0
            self.in_link_dict = {}
            self.entry_finder = {}
            for item in seed_list:
                entry = [-1000, self.count, item]
                heapq.heappush(self.heap, entry)
                self.entry_finder[item] = entry
                self.count += 1
                self.in_link_dict[item] = set()
        else:
            # continue from last run
            print "Reading from heap"
            with open("d:/logs/heap_" + str(loop_cnt) + ".log", "r") as fheap:
                self.heap = pickle.load(fheap)
            print "Reading from count"
            with open("d:/logs/count_" + str(loop_cnt) + ".log", "r") as fcount:
                self.count = pickle.load(fcount)
            print "Reading from entry finder"
            with open("d:/logs/entries_" + str(loop_cnt) + ".log", "r") as fentry:
                self.entry_finder = pickle.load(fentry)
            print "Reading from frontier(in_link_dict)"
            with open("d:/logs/frontier_" + str(loop_cnt) + ".log", "r") as ffront:
                self.in_link_dict = pickle.load(ffront)

            print "\nRead successful for count: ", loop_cnt, "\n"

    # This function pushes the given url in the frontier set:
    def push(self, item, in_link):
        priority = 1
        entry = [-priority, self.count, item]
        heapq.heappush(self.heap, entry)
        self.entry_finder[item] = entry
        self.count += 1
        self.in_link_dict[item] = {in_link}

    # This function pops the url with the following priority:
    # seed links first.
    # url with most in links.
    # earlier pushed link.
    def pop(self):
        while self.heap:
            priority, count, item = heapq.heappop(self.heap)
            # print priority, count, item
            if item != 'NA':
                in_link_set = self.in_link_dict[item]
                del self.entry_finder[item]
                del self.in_link_dict[item]
                return item, in_link_set
            else:
                # print "cancelling.. ", priority, count, item
                pass

    # check whether the frontier and seed set is empty or not.
    def is_front_empty(self):
        return len(self.heap) == 0

    # update item in frontier set with newly discovered in-link
    def update(self, item, in_link):
        # print item in self.entry_finder
        entry = self.entry_finder.pop(item)
        self.heap.remove(entry)
        # entry[-1] = 'NA'
        new_priority = -entry[0] + 1
        updated_entry = [-new_priority, entry[1], item]

        heapq.heappush(self.heap, updated_entry)
        self.entry_finder[item] = updated_entry
        self.in_link_dict[item].add(in_link)
        # print "update done.. ", updated_entry

    """ check whether item exists in frontier and seed set or not. """
    def exists(self, item):
        if self.in_link_dict.get(item) is None:
            return False
        else:
            return True

    # logging for debugging purpose
    def write_logs(self, loop_count):
        loop_count = str(loop_count)
        # print "There are ", len(self.in_link_dict), " items in frontier"
        print "Writing to frontier(in_link_dict)"
        p = pickle.Pickler(open("d:/logs/frontier_" + loop_count + ".log", "w"))
        p.fast = True
        p.dump(self.in_link_dict) # d is your dictionary
        p.clear_memo()
        print "Writing to entry finder"
        p = pickle.Pickler(open("d:/logs/entries_" + loop_count + ".log", "w"))
        p.fast = True
        p.dump(self.entry_finder) # d is your dictionary
        p.clear_memo()
        print "Writing to heap"
        p = pickle.Pickler(open("d:/logs/heap_" + loop_count + ".log", "w"))
        p.fast = True
        p.dump(self.heap) # d is your dictionary
        p.clear_memo()
        print "Writing to count"
        with open("d:/logs/count_" + loop_count + ".log", "w") as fcount:
            pickle.dump(self.count, fcount)


        print "\nWrite successful for count: ", loop_count, "\n"

    def fetch_heap(self):
        # self.frontier_clean()
        return self.heap
