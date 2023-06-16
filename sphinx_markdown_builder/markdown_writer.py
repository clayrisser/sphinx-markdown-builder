import os
from typing import List

from docutils import nodes

from .contexts import SubContext, TableContext, AnnotationContext
from .depth import Depth
from .doctree2md import Translator, Writer


class MarkdownTranslator(Translator):
    def __init__(self, document, builder=None):
        Translator.__init__(self, document, builder)
        self.depth = Depth()
        self.enumerated_count = {}
        # Sub context allow us to handle unique cases when post-processing is required
        self.sub_contexts: List[SubContext] = []
        # Saves the current descriptor type
        self.desc_context: List[str] = []

    def reset(self):
        super().reset()
        self.depth = Depth()
        self.enumerated_count = {}
        self.sub_contexts: List[SubContext] = []
        self.desc_context: List[str] = []

    def add_context(self, ctx: SubContext):
        self.sub_contexts.append(ctx)

    def pop_context(self, node):
        content = self.sub_contexts.pop().make()
        self.add(content)

    @property
    def ctx(self) -> SubContext:
        if not len(self.sub_contexts):
            raise nodes.SkipNode
        return self.sub_contexts[-1]

    def add(self, value, section='body'):
        if len(self.sub_contexts) > 0:
            self.sub_contexts[-1].add(value)
        else:
            super().add(value, section)

    def visit_document(self, node):
        pass

    def depart_document(self, node):
        pass

    def visit_title(self, node):
        self.ensure_eol(2)
        self.add((self.section_level * '#') + ' ')

    def visit_desc(self, node):
        self.desc_context.append(node.attributes.get("desctype", ""))

    def depart_desc(self, node):
        self.desc_context.pop()

    def visit_desc_annotation(self, node):
        # annotation, e.g 'method', 'class', or a signature
        self.add_context(AnnotationContext(node))

    depart_desc_annotation = pop_context

    def visit_desc_addname(self, node):
        # module preroll for class/method
        pass

    def depart_desc_addname(self, node):
        # module preroll for class/method
        pass

    def visit_desc_name(self, node):
        # name of the class/method
        # Escape "__" which is a formatting string for markdown
        if node.rawsource.startswith("__"):
            self.add('\\')

    def depart_desc_name(self, node):
        if self.desc_context[-1] in ('function', 'method', 'class'):
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

        # We don't want methods to be at the same level as classes,
        # If signature has a non-null class, that's means it is a signature
        # of a class method
        self.ensure_eol()
        if "class" in node.attributes and node.attributes["class"]:
            self.add('#### ')
        else:
            self.add('### ')

    def depart_desc_signature(self, node):
        # the main signature of class/method
        if self.desc_context[-1] in ('function', 'method', 'class'):
            self.add(')')
        self.ensure_eol()

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
        self.ensure_eol(2)

    def depart_field_list(self, node):
        self.ensure_eol(2)

    def visit_field(self, node):
        self.ensure_eol(2)

    def depart_field(self, node):
        self.ensure_eol(1)

    def visit_field_name(self, node):
        # field name, e.g 'returns', 'parameters'
        self.add('* **')

    def depart_field_name(self, node):
        self.add('**')

    def visit_field_body(self, node):
        self.ensure_eol(1)
        self.start_level('    ')

    def depart_field_body(self, node):
        self.finish_level()

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
        self.ensure_eol(2)
        self.add('### ')

    def depart_rubric(self, node):
        """Sphinx Rubric, a heading without relation to the document sectioning
        http://docutils.sourceforge.net/docs/ref/rst/directives.html#rubric."""
        self.ensure_eol(2)

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
        """Sphinx autosummary See http://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html."""
        pass

    def depart_autosummary_table(self, node):
        """Sphinx autosummary See http://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html."""
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

    @property
    def table_ctx(self) -> TableContext:
        ctx = self.ctx
        assert isinstance(ctx, TableContext)
        return ctx

    def visit_table(self, node):
        self.add_context(TableContext(node))

    depart_table = pop_context

    def visit_thead(self, node):
        self.table_ctx.enter_head()

    def depart_thead(self, node):
        self.table_ctx.exit_head()

    def visit_tbody(self, node):
        self.table_ctx.enter_body()

    def depart_tbody(self, node):
        self.table_ctx.exit_body()

    def visit_row(self, node):
        self.table_ctx.enter_row()

    def depart_row(self, node):
        self.table_ctx.exit_row()

    def visit_entry(self, node):
        self.table_ctx.enter_entry()

    def depart_entry(self, node):
        self.table_ctx.exit_entry()

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
        # Make sure the list item ends with a new line
        self.ensure_eol()

    def descend(self, node_name):
        self.depth.descend(node_name)

    def ascend(self, node_name):
        self.depth.ascend(node_name)

class MarkdownWriter(Writer):
    translator_class = MarkdownTranslator
