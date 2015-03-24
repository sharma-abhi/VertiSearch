__author__ = 'Abhijeet Sharma'

import heapq


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

    def __init__(self, seed_list):
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
        entry = self.entry_finder.pop(item)
        # print "in update.. ", entry
        entry[-1] = 'NA'
        new_priority = -entry[0] + 1
        updated_entry = [-new_priority, entry[1], item]
        heapq.heappush(self.heap, updated_entry)
        self.entry_finder[item] = updated_entry
        self.in_link_dict[item].add(in_link)
        # print "update done.. ", updated_entry
        '''entry =[(a, b, c) for a, b, c in self.heap if c == item]
        if len(entry) == 0:
            print "Error in update, item not found"
        else:
            entry = entry[0]
            self.heap.remove(entry)
            self.in_link_dict[item].add(in_link)

            updated_entry = (-new_priority, entry[1], item)
            heapq.heappush(self.heap, updated_entry)'''

    """ check whether item exists in frontier and seed set or not. """
    def exists(self, item):
        if self.in_link_dict.get(item) is None:
            return False
        else:
            return True

    # logging for debugging purpose
    def write_logs(self, loop_count):
        with open("logs/frontier_" + str(loop_count) + ".log","w") as flog:
            flog.write(str(self.in_link_dict))
        print "There are ", len(self.in_link_dict), " items in frontier"

'''
class FrontierQueue:
    """Seed URLs should always be crawled first.
    Prefer pages with higher in-link counts.
    If multiple pages have maximal in-link counts, choose the option which has been in the
    queue the longest"""

    def __init__(self, seed_list):
        # initializing frontier and seed sets.
        self.seed = {}
        self.count = {}
        self.counter = 1
        for item in seed_list:
            self.seed[item] = set()
            self.count[item] = self.counter
            self.counter += 1
        self.front = {}


    # This function pushes the given url in the frontier set:
    def push(self, item, in_link):
        self.front[item] = {in_link}
        self.count[item] = self.counter
        self.counter += 1

    # This function pops the url with the following priority:
    # seed links first.
    # url with most in links.
    # earlier pushed link.
    def pop(self):
        # checking frontier set.
        if len(self.seed) == 0:
            #item = sorted(self.front.items(),key=lambda x: len(x[1]))[0][0]
            max_link_num = max([len(item) for item in self.front.values()])
            key_list = [x for x in self.front if len(self.front[x]) == max_link_num]
            min_count_dict = {key: self.count[key] for key in key_list}
            item = sorted(min_count_dict, key=min_count_dict.get)[0]
            in_links = self.front[item]
            del self.front[item]
            del self.count[item]
            return item, in_links
        else:
            # checking seed set.
            max_link_num = max([len(item) for item in self.seed.values()])
            key_list = [x for x in self.seed if len(self.seed[x]) == max_link_num]
            min_count_dict = {key: self.count[key] for key in key_list}
            item = sorted(min_count_dict, key=min_count_dict.get)[0]
            in_links = self.seed[item]
            del self.seed[item]
            del self.count[item]
            return item, in_links

    # check whether the frontier and seed set is empty or not.
    def is_front_empty(self):
        # checking frontier set.
        if len(self.front) == 0:
            # if frontier empty, checking seed set.
            return len(self.seed) == 0
        else:
            return False

    # update item in frontier set with newly discovered in-link
    def update(self, item, in_link):
        if self.front.get(item) is None:
            try: self.seed[item].add(in_link)
            except KeyError as error:
                with open("run_errors.log","a+") as ferr:
                    ferr.write("Error detected in frontier: " + str(error) + "for url: " + str(item) + "\n")
        else:
            self.front[item].add(in_link)

    # check whether item exists in frontier and seed set or not."
    def exists(self, item):
        if self.front.get(item) is None and self.seed.get(item) is None:
            return False
        else:
            return True

    # logging for debugging purpose
    def write_logs(self, loop_count):
        with open("logs/frontier_" + str(loop_count) + ".log","w") as flog:
            flog.write(str(self.front))
        print "There are ", len(self.front), " items in frontier"'''