from .doctree2md import Translator, Writer
from docutils import nodes
from pydash import _
import html2text

h = html2text.HTML2Text()

class MarkdownTranslator(Translator):
    row_entries = []
    rows = []
    tables = []
    tbodys = []
    theads = []

    @property
    def rows(self):
        rows = []
        if not len(self.tables):
            return rows
        for node in self.tables[len(self.tables) - 1].children:
            if isinstance(node, nodes.row):
                rows.append(node)
            else:
                for node in node.children:
                    if isinstance(node, nodes.row):
                        rows.append(node)
        return rows

    def visit_document(self, node):
        print(node)

    def visit_title(self, node):
        self.add((self.section_level) * '#' + ' ')

    def visit_subtitle(self, node):
        self.add((self.section_level + 1) * '#' + ' ')

    def visit_table(self, node):
        self.tables.append(node)

    def depart_table(self, node):
        self.tables.pop()

    def visit_thead(self, node):
        if not len(self.tables):
            raise nodes.SkipNode
        self.theads.append(node)

    def depart_thead(self, node):
        for i in range(len(self.row_entries)):
            length = 0
            for row in self.rows:
                if len(row.children) > i:
                    entry_length = len(row.children[i].astext())
                    if entry_length > length:
                        length = entry_length
            self.add('| ' + ''.join(_.map(range(length), lambda: '-')) + ' ')
        self.add('|\n')
        self.row_entries = []
        self.theads.pop()

    def visit_tbody(self, node):
        if not len(self.tables):
            raise nodes.SkipNode
        self.tbodys.append(node)

    def depart_tbody(self, node):
        self.tbodys.pop()

    def visit_row(self, node):
        if not len(self.theads) and not len(self.tbodys):
            raise nodes.SkipNode
        self.rows.append(node)

    def depart_row(self, node):
        self.add('|\n')
        if not len(self.theads):
            self.row_entries = []
        self.rows.pop()

    def visit_entry(self, node):
        if not len(self.rows):
            raise nodes.SkipNode
        self.row_entries.append(node)
        self.add('| ')

    def depart_entry(self, node):
        length = 0
        i = len(self.row_entries) - 1
        for row in self.rows:
            if len(row.children) > i:
                entry_length = len(row.children[i].astext())
                if entry_length > length:
                    length = entry_length
        padding = ''.join(_.map(range(length - len(node.astext())), lambda: ' '))
        self.add(padding + ' ')

class MarkdownWriter(Writer):
    translator_class = MarkdownTranslator
