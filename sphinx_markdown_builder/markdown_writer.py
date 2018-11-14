from .doctree2md import Translator, Writer

class MarkdownTranslator(Translator):
    def visit_title(self, node):
        self.add((self.section_level) * '#' + ' ')

    def visit_subtitle(self, node):
        self.add((self.section_level + 1) * '#' + ' ')

class MarkdownWriter(Writer):
    translator_class = MarkdownTranslator
