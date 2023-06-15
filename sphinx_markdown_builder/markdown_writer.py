import os
from typing import List

from tabulate import tabulate
from docutils import nodes

from .depth import Depth
from .doctree2md import Translator, Writer


class TableHandler:
    def __init__(self):
        self.is_head = False
        self.is_body = False
        self.is_row = False
        self.is_entry = False

        self.headers = []
        self.body = []

    def enter_head(self):
        assert not self.is_body
        self.is_head = True

    def exit_head(self):
        assert self.is_head
        self.is_head = False

    def enter_body(self):
        assert not self.is_head
        self.is_body = True

    def exit_body(self):
        assert self.is_body
        self.is_body = False

    def get_output(self):
        if self.is_head:
            return self.headers
        else:
            assert self.is_body
            return self.body

    def enter_row(self):
        assert self.is_head or self.is_body
        self.is_row = True
        self.get_output().append([])

    def exit_row(self):
        assert self.is_row
        self.is_row = False

    def enter_entry(self):
        assert self.is_row
        self.is_entry = True
        self.get_output()[-1].append([])

    def exit_entry(self):
        assert self.is_entry
        self.is_entry = False

    def add(self, value):
        assert self.is_entry
        self.get_output()[-1][-1].append(value)

    @staticmethod
    def make_row(row):
        return ["".join(entries) for entries in row]

    def make_table(self):
        if len(self.headers) == 0 and len(self.body) == 0:
            return ""

        if len(self.headers) == 0:
            headers = ["" for _ in self.body[0]]
        else:
            assert len(self.headers) == 1
            headers = self.make_row(self.headers[0])

        body = list(map(self.make_row, self.body))
        return tabulate(body, headers=headers, tablefmt="github")


class MarkdownTranslator(Translator):
    def __init__(self, document, builder=None):
        Translator.__init__(self, document, builder)
        self.builder = builder
        self.depth = Depth()
        self.enumerated_count = {}
        self.tables: List[TableHandler] = []

    def add(self, value, section='body'):
        if len(self.tables) > 0:
            self.tables[-1].add(value)
        else:
            super().add(value, section)

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
        # annotation, e.g 'method', 'class', or a signature
        stripped = self.get_current_output('body')[-1].strip()
        self.get_current_output('body')[-1] = stripped
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

        # Insert anchors if enabled by the builder
        if self.builder.insert_anchors_for_signatures:
            for sig_id in node.get("ids", ()):
                self.add('<a name="{}"></a>'.format(sig_id))

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

        alt = node.attributes.get('alt', 'image')
        # We don't need to add EOL before/after the image.
        # It will be handled by the visit/depart handlers of the paragraph.
        self.add(f'![{alt}]({uri})')

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

    def cur_table(self) -> TableHandler:
        if not len(self.tables):
            raise nodes.SkipNode
        return self.tables[-1]

    def visit_table(self, node):
        self.tables.append(TableHandler())

    def depart_table(self, node):
        last_table = self.tables.pop()
        self.add(last_table.make_table())

    def visit_thead(self, node):
        self.cur_table().enter_head()

    def depart_thead(self, node):
        self.cur_table().exit_head()

    def visit_tbody(self, node):
        self.cur_table().enter_body()

    def depart_tbody(self, node):
        self.cur_table().exit_body()

    def visit_row(self, node):
        self.cur_table().enter_row()

    def depart_row(self, node):
        self.cur_table().exit_row()


    def visit_entry(self, node):
        self.cur_table().enter_entry()

    def depart_entry(self, node):
        self.cur_table().exit_entry()

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
        depth_padding = '    ' * (depth - 1)
        marker = '*'
        if node.parent.tagname == 'enumerated_list':
            if depth not in self.enumerated_count:
                self.enumerated_count[depth] = 1
            else:
                self.enumerated_count[depth] = self.enumerated_count[depth] + 1
            marker = str(self.enumerated_count[depth]) + '.'
        # Make sure the list item prefix starts at a new line
        self.ensure_eol()
        self.add(depth_padding + marker + " ")

    def depart_list_item(self, node):
        self.depth.ascend('list_item')
        # Make sure the list item end with a new line
        self.ensure_eol()

    def descend(self, node_name):
        self.depth.descend(node_name)

    def ascend(self, node_name):
        self.depth.ascend(node_name)

class MarkdownWriter(Writer):
    translator_class = MarkdownTranslator
