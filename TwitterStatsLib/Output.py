""" Module providing standard output classes """

from abc import ABCMeta, abstractmethod
from mako.template import Template

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
        for key in data.keys():
            text = text.replace(key, 'data[\'' + key + '\']')
        return text

    def render(self, data):
        """ Render HTML file """
        mako_template = Template(filename='html_template.mako', module_directory='tmp/',
                                 preprocessor=lambda text: self._preprocess(text, data))
        return mako_template.render_unicode(data=data)
