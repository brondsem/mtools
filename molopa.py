#!/usr/bin/python

import argparse, re
from filters import WordFilter, SlowFilter, DateTimeFilter


class MongoLogParser:

    def __init__(self):
        self.filters = []        

    def addFilter(self, filterClass):
        """ adds a filter class to the parser. """
        if not filterClass in self.filters:
            self.filters.append(filterClass)

    def _arrayToString(self, arr):
        """ if arr is of type list, join elements with space delimiter. """
        if isinstance(arr, list):
            return " ".join(arr)
        else:
            return arr

    def parse(self):
        """ parses the logfile and asks each filter if it accepts the line.
            it will only be printed if all filters accept the line.
        """

        # create parser object
        parser = argparse.ArgumentParser(description='mongod/mongos log file parser.')
        parser.add_argument('logfile', action='store', help='logfile to parse')
        
        # add arguments from filter classes
        for f in self.filters:
            for fa in f.filterArgs:
                parser.add_argument(fa[0], **fa[1])

        args = vars(parser.parse_args())
        args = dict((k, self._arrayToString(args[k])) for k in args)
        
        # create filter objects from classes and pass args
        self.filters = [f(args) for f in self.filters]

        # remove non-active filter objects
        self.filters = [f for f in self.filters if f.active]

        # open logfile
        logfile = open(args['logfile'], 'r')

        # go through each line and ask each filter if it accepts
        for line in logfile:

            # special case: if line starts with ***, always print (server restart)
            if line.startswith('***'):
                print line,
                continue

            # only print line if all filters agree
            if all([f.accept(line) for f in self.filters]):
                print line,

            # if at least one filter refuses to print remaining lines, stop
            if any([f.skipRemaining() for f in self.filters]):
                break



if __name__ == '__main__':

    # create MongoLogParser instance
    molopa = MongoLogParser()

    # add filters
    molopa.addFilter(SlowFilter)
    molopa.addFilter(WordFilter)
    molopa.addFilter(DateTimeFilter)
    
    # start parsing
    molopa.parse()









    