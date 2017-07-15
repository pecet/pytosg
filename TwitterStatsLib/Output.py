""" Module providing standard output classes """

import re
from abc import ABCMeta, abstractmethod
from mako.template import Template
from mako.lookup import TemplateLookup

class Output(object):
    """ Abstract class base for output classes """
    __metaclass__ = ABCMeta

    @abstractmethod
    def render(self, data):
        """ Render passed data """
        pass


class HTMLOutput(Output):
    """ HTML output renderer, using Mako templates """

    def _preprocess(self, text, data):
        """ Preprocess mako template, to automatically access data dictionary
            as we cannot unpack data in render_unicode directly using ** operator
            because unpacking is accessing individual items via __getitem__
            advantages of LazyDict

            Because of this preprocessing you can write in mako template e.g.:
            ${tweet_count_total}
            Instead of:
            ${data['tweet_count_total']}
            """

        regex_str = ''
        for key in data.keys():
            regex_str += r'\b' + key + r'\b|'
        regex_str = r'((?:' + regex_str[:-1] + r')+)'
        regex = re.compile(regex_str)
        text = regex.sub(r"data['\1']", text)
        return text

    def render(self, data):
        """ Render HTML file """
        template_lookup = TemplateLookup(directories=['templates/'],
                                         module_directory='tmp/',
                                         preprocessor=lambda text: self._preprocess(text, data))
        mako_template = template_lookup.get_template('html_template.mako')
        return mako_template.render_unicode(data=data)
