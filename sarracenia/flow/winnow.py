import sarracenia.moth
import copy
from sarracenia.flow import Flow
import logging

logger = logging.getLogger(__name__)

default_options = {'accept_unmatched': True, 'nodupe_ttl': 300}


class Winnow(Flow):
    def __init__(self, options):

        super().__init__(options)
        self.plugins['load'].append('sarracenia.flowcb.gather.message.Message')
        self.plugins['load'].append('sarracenia.flowcb.post.message.Message')
