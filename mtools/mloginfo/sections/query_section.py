from base_section import BaseSection

from mtools.util.profile_collection import ProfileCollection
from mtools.util.grouping import Grouping
from mtools.util.print_table import print_table
from mtools.util import OrderedDict

from operator import itemgetter

import numpy as np

class QuerySection(BaseSection):
    """ 
    """
    
    name = "queries"

    def __init__(self, mloginfo):
        BaseSection.__init__(self, mloginfo)

        # add --queries flag to argparser
        self.mloginfo.argparser_sectiongroup.add_argument('--queries', action='store_true', help='outputs statistics about query patterns')

        # progress bar
        self.progress_bar_enabled = not self.mloginfo.is_stdin


    @property
    def active(self):
        """ return boolean if this section is active. """
        return self.mloginfo.args['queries']


    def run(self):
        """ run this section and print out information. """
        grouping = Grouping(group_by=lambda x: (x.namespace, x.pattern))
        logfile = self.mloginfo.logfile

        if logfile.start and logfile.end:
            progress_start = self.mloginfo._datetime_to_epoch(logfile.start)
            progress_total = self.mloginfo._datetime_to_epoch(logfile.end) - progress_start
        else:
            self.progress_bar_enabled = False


        for i, le in enumerate(logfile):
            # update progress bar every 1000 lines
            if self.progress_bar_enabled and (i % 1000 == 0):
                if le.datetime:
                    progress_curr = self.mloginfo._datetime_to_epoch(le.datetime)
                    self.mloginfo.update_progress(float(progress_curr-progress_start) / progress_total)

            if le.operation in ['query', 'update', 'remove']:
                grouping.add(le)

        grouping.sort_by_size()

        # clear progress bar again
        self.mloginfo.update_progress(1.0)

        titles = ['namespace', 'pattern', 'count', 'min (ms)', 'max (ms)', 'mean (ms)', 'sum (ms)']
        table_rows = []
        for g in grouping:
            # calculate statistics for this group
            namespace, pattern = g

            group_events = [le.duration for le in grouping[g] if le.duration != None]

            stats = OrderedDict()
            stats['namespace'] = namespace
            stats['pattern'] = pattern
            stats['count'] = len( group_events )
            stats['min'] = min( group_events ) if group_events else '-'
            stats['max'] = max( group_events ) if group_events else '-'
            stats['mean'] = 0
            stats['sum'] = sum( group_events ) if group_events else '-'
            stats['mean'] = stats['sum'] / stats['count'] if group_events else '-'

            if self.mloginfo.args['verbose']:
                stats['example'] = grouping[g][0]
                titles.append('example')

            table_rows.append(stats)

        table_rows = sorted(table_rows, key=itemgetter('sum'), reverse=True)
        print_table(table_rows, titles, uppercase_headers=False)
        print 

