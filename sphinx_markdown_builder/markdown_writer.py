from .depth import Depth
from .doctree2md import Translator, Writer

import html2text
import os
import sys
import posixpath
from typing import TYPE_CHECKING, Iterable, List, Tuple, cast
from docutils import nodes
from docutils.nodes import Element, Node, Text
from pydash import _
from sphinx.application import Sphinx
from typing import cast
from sphinx.util import logging, progress_message
from sphinx.locale import __
from sphinx.builders import Builder
from sphinx.util.docutils import SphinxTranslator

if TYPE_CHECKING:
    from .markdown_builder import MarkdownBuilder


h = html2text.HTML2Text()
logger = logging.getLogger(__name__)
###
#   this_doc = self.builder.current_docname


class MarkdownTranslator(SphinxTranslator,Translator):
    builder: "MarkdownBuilder" = None
    depth = Depth()
    enumerated_count = {}
    table_entries = []
    table_rows = []
    tables = []
    tbodys = []
    theads = []

    
    def __init__(self, document: nodes.document, builder: Builder) -> None:
        super().__init__(document, builder)
        self.builder = builder
        
        self.numfig = self.config.numfig
        self.numfig_format = self.config.numfig_format
        self.docnames = [self.builder.current_docname]

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


    def _toParent (self, node, node_type, max_levels=10):
        curNode = node
        level = max_levels
        while not isinstance(curNode, node_type) and level > 0 and curNode:
            curNode = curNode.parent
            level -= 1
        if level < 0:
            curNode = None            
        return curNode


    def visit_start_of_file(self, node: Element):
        self.docnames.append(node['docname'])

    def depart_start_of_file(self, node: Element):
        self.docnames.pop()

    def visit_document(self, node):
        pass

    def depart_document(self, node):
        pass

    def visit_title(self, node):
        print(">>>> VISIT TITLE", node.parent)
        #  Table title means table caption
        if isinstance(node.parent,nodes.table):
            self.add('*')
            s=self.get_fignumber(node.parent)
            self.add(s+ '. ')        
        else:
            self.add((self.section_level) * '#' + ' ')
            
    def depart_title(self, node):
        if isinstance(node.parent,nodes.table):
            self.add('*\n')    
        else:
            self.ensure_eol()
            self.add('\n') 

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
        olduri = node['uri']
        # rewrite the URI if the environment knows about it
        if olduri in self.builder.images:
            node['uri'] = posixpath.join(self.builder.imgpath,
                                         self.builder.images[olduri])
        uri = node['uri']
        
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
        self.table_rows=[]
        self.table_entries=[]
        # TO_DO:
        for sig_id in node.get("ids", ()):
            self.add('<a name="{}"></a>'.format(sig_id))
        print(">>>> VISIT TABLE: ", node)

    def depart_table(self, node):
        ##  Better readable when table and folowing text are devided by line
        self.add('\n')
        self.tables.pop()
        print(">>>> DEPART TABLE")

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
        print(">>>>> VISIT THEAD :", node)
        print(">>>>> theads : ", self.theads)



    def depart_thead(self, node):
        # nList = node.parent.traverse()
        for iNode in node.parent.traverse():
            if isinstance(iNode, nodes.colspec):
                w = cast(nodes.Element,iNode).get("colwidth")
                self.add('| ' + ''.join(_.map(range(w), lambda: '-')) + ' ')
        
        # for i in range(len(self.table_entries)):
        #     length = 0
        #     for row in self.table_rows:
        #         if len(row.children) > i:
        #             entry_length = len(row.children[i].astext())
        #             if entry_length > length:
        #                 length = entry_length
        #     self.add('| ' + ''.join(_.map(range(length), lambda: '-')) + ' ')
        self.add('|\n')
        self.table_entries = []
        self.theads.pop()
        # print(">>>>>> DEPART THEAD")
        # print(">>>>>> theads : ",self.theads)

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
        # print(">>>>>> VISIT ROW : ",node)
        # print(">>>>>> row : ",self.table_rows)

    def depart_row(self, node):
        self.add('|\n')
        if not len(self.theads):
            self.table_entries = []
        # print(">>>>>> DEPART ROW : ")
        # print(">>>>>> row : ",self.table_rows)

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
        # print(">>>>>> VISIT ENTRY : ",node)
        # print(">>>>>> table_entries : ",self.table_entries)

    def depart_entry(self, node):
        ###  On depart table entry, try to find columnn width specification from heade and calculate this colemn width
        padding = ''
        colSpecs = self._toParent(node,nodes.table).traverse(nodes.colspec)
        # colSpecs = list(filter(lambda x: isinstance(x, nodes.colspec), self._toParent(node,nodes.table).traverse()))
        pos = len(self.table_entries) - 1
        if pos > len(colSpecs)-1:
            logger.warning(__('Columns count out of range found headers. Got ',pos,'columns'))    
        wspc = list(colSpecs)[pos].get("colwidth") - len(node.astext())
        if wspc > 0:
            padding = ''.join(_.map(range(wspc), lambda: ' '))
                                                 
        self.add(padding + ' ')


    def descend(self, node_name):
        self.depth.descend(node_name)

    def ascend(self, node_name):
        self.depth.ascend(node_name)


    def visit_caption(self, node: Element):
        print(">>>> VISIT CAPTION ", node.parent)
        if self.builder.md_insert_html:
            self.add('<span class="caption">')
        self.add('*'+self.get_fignumber(node.parent) + ' ')

    def depart_caption(self, node: Element):
        self.add('*') 
        if self.builder.md_insert_html:
            self.add('</span>\n')
   
    
    
    def visit_figure(self, node: Element):
        print(">>>> VISIT FIGURE ", node)
        
        if self.builder.md_insert_html:
            self.add('<div class="figure" style="')
            if node.get('width'):
                self.add('width: %s;' % node['width'])
            if node.get('align'):
                self.add('align-%s;' % node['align'])
            self.add('">\n')    

        # rewrite the URI if the environment knows about it
        # olduri = node['uri']
        # if olduri in self.builder.images:
        #     node['uri'] = posixpath.join(self.builder.imgpath,
        #                                  self.builder.images[olduri])
        # uri = node['uri']
        
        # doc_folder = os.path.dirname(self.builder.current_docname)
        # if uri.startswith(doc_folder):
        #     # drop docname prefix
        #     uri = uri[len(doc_folder):]
        #     if uri.startswith('/'):
        #         uri = '.' + uri
        # self.add('\n\n![image](%s)\n\n' % uri)
    
    def depart_figure(self, node):
        if self.builder.md_insert_html:
            self.add('</div>\n')

    def get_fignumber(self, node: Element):
        strNumber = ''
        figtype = self.builder.env.domains['std'].get_enumerable_node_type(node)
        idList = node['ids']

        if not figtype: 
            return None
        
        if len(idList) == 0:
            msg = __('Any IDs not assigned for %s node') % node.tagname
            logger.warning(msg, location=node)
            return None
        
        figure_id = node['ids'][0]
        
        # print (">>>>GET FIGNUMBER figtype=",figtype,
        #     "\n     idList=",idList,
        #     "\n     figure_id=",figure_id,
        #     "\n     fignumbers=",self.builder.fignumbers,
        #     "\n     fignumbers2=",self.builder.fignumbers.get(figtype, {})
        #     )
        
        if figure_id in self.builder.fignumbers.get(figtype, {}):
            prefix = self.config.numfig_format.get(figtype)
            if prefix is None:
                msg = __('numfig_format is not defined for %s') % figtype
                logger.warning(msg)
                return None
            else:
                strNumber  = '.'.join(map(str,self.builder.fignumbers[figtype][figure_id]))
                
        # print('Gen new number=%s' % strNumber, ", for tag ",figtype)   
        if  strNumber:
            logger.debug('Gen new number=%s' % strNumber, ", for tag ",figtype )
            return prefix % strNumber    
        else:
            logger.warn('File %s. Numfig not found id=%s, tag=%s' % (self.builder.current_docname,figure_id,figtype))
            return ''      
                     

        
        
     
    def add_secnumber(self, node: Element):
        secnumber = self.get_secnumber(node)
        
        if secnumber:
            print (">>>> ADD add_secnumber:", map(str, secnumber)) 


    def get_secnumber(self, node: Element) -> Tuple[int, ...]:
        if node.get('secnumber'):
            return node['secnumber']
        elif isinstance(node.parent, nodes.section):
            if self.builder.name == 'singlehtml':
                docname = self.docnames[-1]
                anchorname = "%s/#%s" % (docname, node.parent['ids'][0])
                if anchorname not in self.builder.secnumbers:
                    anchorname = "%s/" % docname  # try first heading which has no anchor
            else:
                anchorname = '#' + node.parent['ids'][0]
                if anchorname not in self.builder.secnumbers:
                    anchorname = ''  # try first heading which has no anchor

            if self.builder.secnumbers.get(anchorname):
                return self.builder.secnumbers[anchorname]

        return None


class MarkdownWriter(Writer):
    # supported = ('md', 'markdown')
    translator_class = MarkdownTranslator

    # def __init__(self, builder: "MarkdownBuilder"):
    #     super().__init__()
    #     self.builder = builder
  
        