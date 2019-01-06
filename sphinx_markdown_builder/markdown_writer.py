from .doctree2md import Translator, Writer

class MarkdownTranslator(Translator):

    def __init__(self, document, builder=None):
        Translator.__init__(self, document, builder=None)
        self.builder = builder
        self.rendering_table = False
        self.num_table_colums = 0


    def visit_document(self, node):
        # do nothing

    def depart_document(self, node):
        variables = {
            'layout': 'default',
            'title': self.builder.env.longtitles[self.builder.current_docname].astext()
        }

        # figure our parent
        parent = self.builder.parents.get(self.builder.current_docname)
        if parent:
            variables['parent'] = self.builder.env.longtitles[parent].astext()

        # figure out our grandparent
        grandparent = self.builder.grandparents.get(self.builder.current_docname)
        if grandparent:
            variables['grand_parent'] = self.builder.env.longtitles[grandparent].astext()

        # figure out if we have children
        if self.builder.current_docname in self.builder.parents.itervalues():
            # our page is declared as a parent page
            variables['has_children'] = 'true'

        frontmatter = ['---']
        for (k, v) in variables.iteritems():
            frontmatter.append('{}: {}'.format(k, v))
        frontmatter.append('---')
        frontmatter.append('')

        self.add("\n".join(frontmatter), section='head')
        Translator.depart_document(self, node)

    def visit_title(self, node):
        self.add((self.section_level) * '#' + ' ')

    def visit_Text(self, node):
        # overridden from base class implementation
        # to handle table rendering
        if self.rendering_table:
            # when rendering tables, make sure
            # we remove all whitespace from running text
            text = node.astext()
            text = text.replace("\n", "")
            self.add(text)
        else:
            Translator.visit_Text(self, node)

    def depart_paragraph(self, node):
        # overridden from base class implementation
        # to handle table rendering

        # opt out of default behaviour of
        # adding a line break after paragraphs
        # if we are inside a table construct
        if not self.rendering_table:
            Translator.depart_paragraph(self, node)



    def __placeholder(self, node, is_entry=True):
        self.add('`<%s>`\n' % (node.__class__))
        # print "VISIT %s: %s" % (node.__class__, node)
        # self.add('%s: %s' % (node.__class__, node.astext()))



    # auto formatting of code

    # classes:
    #
    # desc [desctype='class', objtype='class']
    #   desc_signature [fullname='MyClass', ids='full_module.path.to.MyClass', module='full_module_path.to'
    #       desc_annotation (e.g. 'class')
    #       desc_addname (e.g. 'full_module.path.to.'
    #       desc_name (e.g. 'MyClass')
    #       desc_parameterlist
    #           desc_parameter
    #       comment
    #   desc_content

    # methods:
    #
    #






    def visit_desc(self, node):
        # auto doc
        #self.add("\n\n```")
        #self.add(node.pformat())
        #self.add("```\n\n")
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
        self.add('\n\n[!image](%s)\n\n' % uri)

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
        self.add("\n")
        self.rendering_table = True

    def depart_table(self, node):
        self.add("\n\n")
        self.rendering_table = False

    def visit_colspec(self, node):
        pass

    def depart_colspec(self, node):
        pass

    def visit_tgroup(self, node):
        self.num_table_colums = node.attributes['cols']

    def depart_tgroup(self, node):
        pass

    def visit_thead(self, node):
        pass

    def depart_thead(self, node):
        pass

    def visit_tbody(self, node):
        # markdown tables require a header (thead)
        # inject one if missing
        tgroup_node = node.parent
        if 'thead' not in [x.__class__.__name__ for x in tgroup_node.children]:
            header = " | ".join(["   "] * self.num_table_colums)
            self.add("| %s |\n" % header)

        # add table header/body separation
        header = " | ".join(["---"] * self.num_table_colums)
        self.add("| %s |\n" % header )

    def depart_tbody(self, node):
        pass

    def visit_row(self, node):
        self.add('| ')

    def depart_row(self, node):
        self.add("\n")

    def visit_entry(self, node):
        pass

    def depart_entry(self, node):
        self.add(' | ')

    def visit_tabular_col_spec(self, node):
        pass

    def depart_tabular_col_spec(self, node):
        pass



class MarkdownWriter(Writer):
    translator_class = MarkdownTranslator
