from .depth import Depth
from .doctree2md import Translator, Writer

import html2text
import os
import sys
import posixpath
import re
# import string
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

if sys.version_info >= (3, 0):
    from urllib.request import url2pathname
else:
    from urllib import url2pathname

if sys.version_info >= (3, 0):
    unicode = str  # noqa


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
    special_characters = {ord('&'): u'&amp;',
                          ord('<'): u'&lt;',
                          ord('"'): u'&quot;',
                          ord('>'): u'&gt;',
                          ord('@'): u'&#64;', # may thwart address harvesters
                         }
    """Character references for characters with a special meaning in HTML."""

    
    def __init__(self, document: nodes.document, builder: Builder):
        super().__init__(document, builder)
        self.builder = builder
        
        self.numfig = self.config.numfig
        self.numfig_format = self.config.numfig_format
        self.docnames = []
        


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

    def encode(self, text):
        """Encode special characters in `text` & return."""
        # Use only named entities known in both XML and HTML
        # other characters are automatically encoded "by number" if required.
        # @@@ A codec to do these and all other HTML entities would be nice.
        text = unicode(text)
        return text.translate(self.special_characters)

   
    def set_anchor(self,node):
        if self.builder.md_insert_html and node and len(node['ids']) != 0:
            for id in node['ids']:
                self.add('<a name={}></a>'.format(id))
            self.add('\n')
        
   
   
   
    #####################################################################################
    ##
    ##    FILE, DOCUMENT, HEADERS PROCESSING
    ##
    #####################################################################################


    def visit_start_of_file(self, node: Element):
        self.docnames.append(node['docname'])

            
    def depart_start_of_file(self, node: Element):
        self.docnames.pop()

    def visit_document(self, node):
        pass

    def depart_document(self, node):
        pass


    def visit_section(self, node):
        # print(">>>> VISIT SECTION ",node)
        self.set_anchor(node)
        return super().visit_section(node)




    def visit_title(self, node):
        # print(">>>> VISIT TITLE", node.parent)
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
                   
    #####################################################################################
    ##
    ##    SIMPLE TEXT TAGS
    ##
    #####################################################################################
    def depart_paragraph(self, node):
        ## Inside table cell does not need to add line break
        if type(node.parent) != nodes.entry:
            self.ensure_eol()
            self.add('\n')        

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
        print (">>>> VISIT TITLE_REFERENCE")
        pass

    def depart_title_reference(self, node):
        pass


    def visit_literal(self, node):
        print (">>>> VISIT LITERAL", node)
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


    ################################################################################
    ###
    ###      PICTURES PROCESSING
    ###
    ################################################################################

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

    
    def visit_figure(self, node: Element):
        print(">>>> VISIT FIGURE ", node)
        
        self.set_anchor(node)
            
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


    ################################################################################
    ###
    ###      TABLE PROCESSING
    ###
    ################################################################################

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
        self.table_rows=[]
        self.table_entries=[]
        
        self.set_anchor(node)
        # print(">>>> VISIT TABLE: ", node)

    def depart_table(self, node):
        ##  Better readable when table and folowing text are devided by line
        self.add('\n')
        self.tables.pop()
        # print(">>>> DEPART TABLE")

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
        # print(">>>>>> VISIT ROW : ",node)
        # print(">>>>>> row : ",self.table_rows)

    def depart_row(self, node):
        self.add('|\n')
        if not len(self.theads):
            self.table_entries = []
        # print(">>>>>> DEPART ROW : ")
        # print(">>>>>> row : ",self.table_rows)

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

    def visit_autosummary_table(self, node):
        """Sphinx autosummary See http://www.sphinx-
        doc.org/en/master/usage/extensions/autosummary.html."""
        pass

    def depart_autosummary_table(self, node):
        """Sphinx autosummary See http://www.sphinx-
        doc.org/en/master/usage/extensions/autosummary.html."""
        pass


    ################################################################################
    ###
    ###   Various type block processing
    ###
    ################################################################################

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
   
   
    def visit_math_block(self, node):
        pass

    def depart_math_block(self, node):
        pass

    def visit_raw(self, node):
        self.descend('raw')

    def depart_raw(self, node):
        self.ascend('raw')


    ################################################################################
    ###
    ###      LISTS  PROCESSING
    ###
    ################################################################################

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
            marker = unicode(self.enumerated_count[depth]) + '.'
        self.add('\n' + depth_padding + marker + ' ')

    def depart_list_item(self, node):
        self.depth.ascend('list_item')


    ################################################################################
    ###
    ###      LINKS and REFERENCE PROCESSING
    ###
    ################################################################################
    
 
    # def visit_pending_xref(self, node: Element):
    #     print (">>>>VISIT PENDING_XFER ", node)
    #     pass    
    
    def visit_reference(self, node):
        if self.builder.md_insert_html:
            target_uri = ''
            if node['internal'] and node['refid']:
                target_uri = "#" + node['refid']
            elif node['refid']:    
                print (">>>>VISIT REFERENCE - EXTERNAL ", node)
                target_uri=node['refid']
            self.add('<a href="{}">'.format(target_uri))
        super().visit_reference(node)
 
        
    def depart_reference(self, node): 
        if self.builder.md_insert_html:
            self.add('</a>')
        super().depart_reference(node)

           
        
        
    # def visit_inline(self, node):
    #     # self.add('<a>')
    #     print (">>>>VISIT INLINE ", node)
        

    # def depart_inline(self, node):
    #     print (">>>>DEPART INLINE ", node)
    #     # self.add('</a>\n')

    ##  see add_fignumber sphinx/writer/html.py
    def get_fignumber(self, node: Element):
        docname = self.builder.current_docname
        strNumber = ''
        figtype = self.builder.env.domains['std'].get_enumerable_node_type(node)
        figtype_key = '%s/%s' % (docname,figtype)
        idList = node['ids']
        
        #
        #                              docname/figtype  {key=t1}
        #   self.builder.fignumbers = {'body/table': {'t1': (1,)}, 'body/figure': {'id2': (1,)}}
        #
        
        if not figtype_key: 
            return None
        
        if len(idList) == 0:
            msg = __('Any IDs not assigned for %s node') % node.tagname
            logger.warning(msg, location=node)
            return None
        
        figure_id = node['ids'][0]
        
        key = figure_id
        # key = '%s/%s' % (self.builder.current_docname, '%s/%s' % (docname,figure_id))
        
        ### figtype  - like 'table' or 'figure'
        ### figure_id  -  like id3
        ###
        # print (">>>>GET FIGNUMBER figtype=",figtype,
        #     "\n     idList=",idList,
        #     "\n     figure_id=",figure_id,
        #     "\n     docname=",self.builder.current_docname,
        #     "\n     figtype_key=",figtype_key,
        #     "\n     key=", key,
        #     "\n     fignumbers=",self.builder.fignumbers,
        #     "\n     all fignumbers2=",self.builder.env.toc_fignumbers
        #     )
        
        if figure_id in self.builder.fignumbers.get(figtype_key):
            # print('key was found in ', self.builder.fignumbers.get(figtype_key))
            # print('Numfig format ', self.config.numfig_format)
            prefix = self.config.numfig_format.get(figtype)
            # print('Get prefix', prefix)
            if prefix is None:
                msg = __('numfig_format is not defined for %s') % figtype
                logger.warning(msg)
                return None
            else:
                strNumber  = '.'.join(map(unicode,self.builder.fignumbers[figtype_key][key]))
                # print('Get strNumber', strNumber)                
                
        # print('Gen new number=%s, for tag "%s"' % (key,figtype))   
        if  strNumber:
            logger.debug('get_fignumber Return "%s"', prefix % strNumber )
            return prefix % strNumber
        else:
            logger.warn('Document "%s". Numfig not found id=%s, tag=%s' % (docname,key,figtype))
            return ''      
                     
     
    def add_secnumber(self, node: Element):
        secnumber = self.get_secnumber(node)
        
        if secnumber:
            print (">>>> ADD add_secnumber:", map(unicode, secnumber)) 


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

    def __init__(self, builder: "MarkdownBuilder"):
        super().__init__()
        self.builder = builder
  
    # def translate(self) -> None:
    #     visitor = self.builder.create_translator(self.document, self.builder)
    #     self.document.walkabout(visitor)
    #     self.output = cast(TextTranslator, visitor).body    