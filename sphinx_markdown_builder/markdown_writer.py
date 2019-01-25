from .doctree2md import Translator, Writer
from docutils import nodes
import html2text

h = html2text.HTML2Text()

class MarkdownTranslator(Translator):
    def visit_title(self, node):
        self.add((self.section_level) * '#' + ' ')

    def visit_subtitle(self, node):
        self.add((self.section_level + 1) * '#' + ' ')

    def visit_raw(self, node):
        text = node.astext()
        if (len(text) >= 35 and text[:35] == '<table border="1" class="docutils">'):
            self.add(h.handle(node.astext()))
            raise nodes.SkipNode

    def depart_raw(self, node):
        pass

class MarkdownWriter(Writer):
    translator_class = MarkdownTranslator
