from .doctree2md import Translator, Writer
from docutils import nodes
from pydash import _
import html2text

h = html2text.HTML2Text()

import os
import sys

class MarkdownTranslator(Translator):
    row_entries = []
    rows = []
    tables = []
    tbodys = []
    theads = []

    def __init__(self, document, builder=None):
        Translator.__init__(self, document, builder=None)
        self.builder = builder

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
        pass

    def depart_document(self, node):
        pass

    def visit_title(self, node):
        self.add((self.section_level) * '#' + ' ')

    def depart_title(self, node):
        super(MarkdownTranslator, self).depart_title(node)

    def visit_desc(self, node):
        pass

    def depart_desc(self, node):
        pass

    def visit_desc_annotation(self, node):
        # annotation, e.g 'method', 'class'
        pass

    def depart_desc_annotation(self, node):
        # annotation, e.g 'method', 'class'
        pass

    def visit_desc_addname(self, node):
        # module preroll for class/method
        pass

    def depart_desc_addname(self, node):
        # module preroll for class/method
        pass

    def visit_desc_name(self, node):
        # name of the class/method
        pass

    def depart_desc_name(self, node):
        # name of the class/method
        self.add("(")

    def visit_desc_content(self, node):
        # the description of the class/method
        pass

    def depart_desc_content(self, node):
        # the description of the class/method
        pass

    def visit_desc_signature(self, node):
        # the main signature of class/method
        self.add("\n#### ")

    def depart_desc_signature(self, node):
        # the main signature of class/method
        self.add(")\n")

    def visit_desc_parameterlist(self, node):
        # method/class ctor param list
        pass

    def depart_desc_parameterlist(self, node):
        # method/class ctor param list
        pass

    def visit_desc_parameter(self, node):
        # single method/class ctr param
        pass

    def depart_desc_parameter(self, node):
        # single method/class ctr param
        # if there are additional params, include a comma
        if node.next_node(descend=False, siblings=True):
            self.add(", ")

    # list of parameters/return values/exceptions
    #
    # field_list
    #   field
    #       field_name (e.g 'returns/parameters/raises')
    #

    def visit_field_list(self, node):
        pass

    def depart_field_list(self, node):
        pass

    def visit_field(self, node):
        self.add("\n")

    def depart_field(self, node):
        self.add("\n")

    def visit_field_name(self, node):
        # field name, e.g 'returns', 'parameters'
        self.add("* **")

    def depart_field_name(self, node):
        self.add("**")

    def visit_literal_strong(self, node):
        self.add("**")

    def depart_literal_strong(self, node):
        self.add("**")

    def visit_literal_emphasis(self, node):
        self.add("*")

    def depart_literal_emphasis(self, node):
        self.add("*")

    def visit_title_reference(self, node):
        pass

    def depart_title_reference(self, node):
        pass

    def visit_versionmodified(self, node):
        # deprecation and compatibility messages
        # type will hold something like 'deprecated'
        self.add("**%s:** " % node.attributes["type"].capitalize())

    def depart_versionmodified(self, node):
        # deprecation and compatibility messages
        pass

    def visit_warning(self, node):
        """
        Sphinx warning directive
        """
        self.add('**WARNING**: ')

    def depart_warning(self, node):
        """
        Sphinx warning directive
        """
        pass

    def visit_note(self, node):
        """
        Sphinx note directive
        """
        self.add('**NOTE**: ')

    def depart_note(self, node):
        """
        Sphinx note directive
        """
        pass

    def visit_rubric(self, node):
        """
        Sphinx Rubric, a heading without relation to the document sectioning
        http://docutils.sourceforge.net/docs/ref/rst/directives.html#rubric
        """
        self.add("### ")

    def depart_rubric(self, node):
        """
        Sphinx Rubric, a heading without relation to the document sectioning
        http://docutils.sourceforge.net/docs/ref/rst/directives.html#rubric
        """
        self.add("\n\n")

    def visit_image(self, node):
        """
        Image directive
        """
        uri = node.attributes['uri']
        doc_folder = os.path.dirname(self.builder.current_docname)
        if uri.startswith(doc_folder):
            # drop docname prefix
            uri = uri[len(doc_folder):]
            if uri.startswith("/"):
                uri = "." + uri
        self.add('\n\n![image](%s)\n\n' % uri)

    def depart_image(self, node):
        """
        Image directive
        """
        pass

    def visit_autosummary_table(self, node):
        """
        Sphinx autosummary
        See http://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html
        """
        pass

    def depart_autosummary_table(self, node):
        """
        Sphinx autosummary
        See http://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html
        """
        pass

    ################################################################################
    # tables
    #
    # docutils.nodes.table
    #     docutils.nodes.tgroup [cols=x]
    #       docutils.nodes.colspec
    #
    #       docutils.nodes.thead
    #         docutils.nodes.row
    #         docutils.nodes.entry
    #         docutils.nodes.entry
    #         docutils.nodes.entry
    #
    #       docutils.nodes.tbody
    #         docutils.nodes.row
    #         docutils.nodes.entry

    def visit_table(self, node):
        self.tables.append(node)

    def depart_table(self, node):
        self.tables.pop()

    def visit_tabular_col_spec(self, node):
        pass

    def depart_tabular_col_spec(self, node):
        pass

    def visit_colspec(self, node):
        pass

    def depart_colspec(self, node):
        pass

    def visit_tgroup(self, node):
        pass

    def depart_tgroup(self, node):
        pass

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
        try:
            self.rows.pop()
        except IndexError:
            pass

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
