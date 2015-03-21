__author__ = 'Abhijeet Sharma'


class FrontierQueue:
    """Seed URLs should always be crawled first.
    Prefer pages with higher in-link counts.
    If multiple pages have maximal in-link counts, choose the option which has been in the
    queue the longest"""

    def __init__(self, seed_list):
        # initializing frontier and seed sets.
        self.seed = {}
        for item in seed_list:
            self.seed[item] = set()
        self.front = {}

    # This function pushes the given url in the frontier set:
    def push(self, item, in_link):
        self.front[item] = set([in_link])

    # This function pops the url with the following priority:
    # seed links first.
    # url with most in links.
    # earlier pushed link.
    def pop(self):
        # checking frontier set.
        if len(self.seed) == 0:
            item = sorted(self.front.items(),key=lambda x: len(x[1]))[0][0]
            in_links = self.front[item]
            del self.front[item]
            return item, in_links
        else:
            # checking seed set.
            item = sorted(self.seed.items(),key = lambda x:len(x[1]))[0][0]
            in_links = self.seed[item]
            del self.seed[item]
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