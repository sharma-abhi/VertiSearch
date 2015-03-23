__author__ = 'Abhijeet Sharma'


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

    # check whether the frontier and seed set is emoty or not.
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
        print "There are ", len(self.front), " items in frontier"