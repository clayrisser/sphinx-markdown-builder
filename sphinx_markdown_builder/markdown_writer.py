from .doctree2md import Translator, Writer
from docutils import nodes
import html2text

h = html2text.HTML2Text()

class MarkdownTranslator(Translator):
    head_entries = 0
    row_depth = 0
    table_depth = 0
    tbody_depth = 0
    thead_depth = 0

    def visit_document(self, node):
        print(node)

    def visit_title(self, node):
        self.add((self.section_level) * '#' + ' ')

    def visit_subtitle(self, node):
        self.add((self.section_level + 1) * '#' + ' ')

    def visit_table(self, node):
        self.table_depth = self.table_depth + 1

    def depart_table(self, node):
        self.table_depth = self.table_depth - 1

    def visit_thead(self, node):
        if not self.table_depth:
            raise nodes.SkipNode
        self.thead_depth = self.thead_depth + 1

    def depart_thead(self, node):
        print('entries: ' + str(self.head_entries))
        for i in range(self.head_entries):
            self.add('| - ')
        self.add('|\n')
        self.head_entries = 0
        self.thead_depth = self.thead_depth - 1

    def visit_tbody(self, node):
        if not self.table_depth:
            raise nodes.SkipNode
        self.tbody_depth = self.tbody_depth + 1

    def depart_tbody(self, node):
        self.tbody_depth = self.tbody_depth - 1

    def visit_row(self, node):
        if not self.thead_depth and not self.tbody_depth:
            raise nodes.SkipNode
        self.row_depth = self.row_depth + 1

    def depart_row(self, node):
        self.add('|\n')
        self.row_depth = self.row_depth - 1

    def visit_entry(self, node):
        if not self.row_depth:
            raise nodes.SkipNode
        self.add('| ')
        if self.thead_depth:
            self.head_entries = self.head_entries + 1

    def depart_entry(self, node):
        self.add(' ')

class MarkdownWriter(Writer):
    translator_class = MarkdownTranslator
