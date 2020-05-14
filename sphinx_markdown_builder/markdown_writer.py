from .depth import Depth
from .doctree2md import Translator, Writer
from docutils import nodes
from pydash import _
import html2text
import os
import sys

h = html2text.HTML2Text()

class MarkdownTranslator(Translator):
    depth = Depth()
    enumerated_count = {}
    table_entries = []
    table_rows = []
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

    def visit_desc(self, node):
        pass

    def depart_desc(self, node):
        pass

    def visit_desc_annotation(self, node):
        # annotation, e.g 'method', 'class'
        self.add('_')

    def depart_desc_annotation(self, node):
        # annotation, e.g 'method', 'class'
        self.get_current_output('body')[-1] = self.get_current_output('body')[-1][:-1]
        self.add('_ ')
    def visit_desc_addname(self, node):
        # module preroll for class/method
        pass

    def depart_desc_addname(self, node):
        # module preroll for class/method
        pass

    def visit_desc_name(self, node):
        # name of the class/method
        # Escape "__" which is a formating string for markdown
        if node.rawsource.startswith("__"):
            self.add('\\')
        pass

    def depart_desc_name(self, node):
        # name of the class/method
        self.add('(')

    def visit_desc_content(self, node):
        # the description of the class/method
        pass

    def depart_desc_content(self, node):
        # the description of the class/method
        pass

    def visit_desc_signature(self, node):
        # the main signature of class/method
        # We dont want methods to be at the same level as classes,
        # If signature has a non null class, thats means it is a signature
        # of a class method
        if ("class" in node.attributes and node.attributes["class"]):
            self.add('\n#### ')
        else:
            self.add('\n### ')

    def depart_desc_signature(self, node):
        # the main signature of class/method
        self.add(')\n')

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
            self.add(', ')

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
        self.add('\n')

    def depart_field(self, node):
        self.add('\n')

    def visit_field_name(self, node):
        # field name, e.g 'returns', 'parameters'
        self.add('* **')

    def depart_field_name(self, node):
        self.add('**')

    def visit_literal_strong(self, node):
        self.add('**')

    def depart_literal_strong(self, node):
        self.add('**')

    def visit_literal_emphasis(self, node):
        self.add('*')

    def depart_literal_emphasis(self, node):
        self.add('*')

    def visit_title_reference(self, node):
        pass

    def depart_title_reference(self, node):
        pass

    def visit_versionmodified(self, node):
        # deprecation and compatibility messages
        # type will hold something like 'deprecated'
        self.add('**%s:** ' % node.attributes['type'].capitalize())

    def depart_versionmodified(self, node):
        # deprecation and compatibility messages
        pass

    def visit_warning(self, node):
        """Sphinx warning directive."""
        self.add('**WARNING**: ')

    def depart_warning(self, node):
        """Sphinx warning directive."""
        pass

    def visit_note(self, node):
        """Sphinx note directive."""
        self.add('**NOTE**: ')

    def depart_note(self, node):
        """Sphinx note directive."""
        pass

    def visit_rubric(self, node):
        """Sphinx Rubric, a heading without relation to the document sectioning
        http://docutils.sourceforge.net/docs/ref/rst/directives.html#rubric."""
        self.add('### ')

    def depart_rubric(self, node):
        """Sphinx Rubric, a heading without relation to the document sectioning
        http://docutils.sourceforge.net/docs/ref/rst/directives.html#rubric."""
        self.add('\n\n')

    def visit_image(self, node):
        """Image directive."""
        uri = node.attributes['uri']
        doc_folder = os.path.dirname(self.builder.current_docname)
        if uri.startswith(doc_folder):
            # drop docname prefix
            uri = uri[len(doc_folder):]
            if uri.startswith('/'):
                uri = '.' + uri
        self.add('\n\n![image](%s)\n\n' % uri)

    def depart_image(self, node):
        """Image directive."""
        pass

    def visit_autosummary_table(self, node):
        """Sphinx autosummary See http://www.sphinx-
        doc.org/en/master/usage/extensions/autosummary.html."""
        pass

    def depart_autosummary_table(self, node):
        """Sphinx autosummary See http://www.sphinx-
        doc.org/en/master/usage/extensions/autosummary.html."""
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

    def visit_math_block(self, node):
        pass

    def depart_math_block(self, node):
        pass

    def visit_raw(self, node):
        self.descend('raw')

    def depart_raw(self, node):
        self.ascend('raw')

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
        self.descend('tgroup')

    def depart_tgroup(self, node):
        self.ascend('tgroup')

    def visit_thead(self, node):
        if not len(self.tables):
            raise nodes.SkipNode
        self.theads.append(node)

    def depart_thead(self, node):
        for i in range(len(self.table_entries)):
            length = 0
            for row in self.table_rows:
                if len(row.children) > i:
                    entry_length = len(row.children[i].astext())
                    if entry_length > length:
                        length = entry_length
            self.add('| ' + ''.join(_.map(range(length), lambda: '-')) + ' ')
        self.add('|\n')
        self.table_entries = []
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
        self.table_rows.append(node)

    def depart_row(self, node):
        self.add('|\n')
        if not len(self.theads):
            self.table_entries = []

    def visit_enumerated_list(self, node):
        self.depth.descend('list')
        self.depth.descend('enumerated_list')

    def depart_enumerated_list(self, node):
        self.enumerated_count[self.depth.get('list')] = 0
        self.depth.ascend('enumerated_list')
        self.depth.ascend('list')

    def visit_bullet_list(self, node):
        self.depth.descend('list')
        self.depth.descend('bullet_list')

    def depart_bullet_list(self, node):
        self.depth.ascend('bullet_list')
        self.depth.ascend('list')

    def visit_list_item(self, node):
        self.depth.descend('list_item')
        depth = self.depth.get('list')
        depth_padding = ''.join(['    ' for i in range(depth - 1)])
        marker = '*'
        if node.parent.tagname == 'enumerated_list':
            if depth not in self.enumerated_count:
                self.enumerated_count[depth] = 1
            else:
                self.enumerated_count[depth] = self.enumerated_count[depth] + 1
            marker = str(self.enumerated_count[depth]) + '.'
        self.add('\n' + depth_padding + marker + ' ')

    def depart_list_item(self, node):
        self.depth.ascend('list_item')

    def visit_entry(self, node):
        if not len(self.table_rows):
            raise nodes.SkipNode
        self.table_entries.append(node)
        self.add('| ')

    def depart_entry(self, node):
        length = 0
        i = len(self.table_entries) - 1
        for row in self.table_rows:
            if len(row.children) > i:
                entry_length = len(row.children[i].astext())
                if entry_length > length:
                    length = entry_length
        padding = ''.join(
            _.map(range(length - len(node.astext())), lambda: ' ')
        )
        self.add(padding + ' ')

    def descend(self, node_name):
        self.depth.descend(node_name)

    def ascend(self, node_name):
        self.depth.ascend(node_name)

class MarkdownWriter(Writer):
    translator_class = MarkdownTranslator
