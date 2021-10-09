from .markdown_writer import MarkdownWriter, MarkdownTranslator
from docutils.io import StringOutput
from docutils import nodes
from docutils.frontend import OptionParser
from docutils.nodes import Node
from io import open
from os import path

from sphinx.builders import Builder
from sphinx.locale import __
from sphinx.util import isurl, logging, md5, progress_message, status_iterator
from sphinx.util.osutil import ensuredir, os_path
from sphinx.application import Sphinx
from sphinx.environment.adapters.asset import ImageAdapter
from sphinx.util.osutil import copyfile, ensuredir, os_path, relative_uri
from typing import IO, Any, Dict, Iterable, Iterator, List, Set, Tuple, Type
from sphinx import addnodes
from sphinx.util.docutils import new_document
from sphinx.util.osutil import ensuredir
from sphinx.util.console import darkgreen  # type: ignore
from sphinx.util.nodes import inline_all_toctrees

from sphinx.transforms.post_transforms import ReferencesResolver

from docutils.nodes import Element
from sphinx.transforms.post_transforms import SphinxPostTransform
from typing import Any, Dict, List, Optional, Sequence, Tuple, Type, cast
from sphinx.errors import NoUri

logger = logging.getLogger(__name__)

class MarkdownBuilder(Builder):
    name = 'markdown'
    format = 'markdown'
    epilog = __('The markdown files are in %(outdir)s.')
    out_suffix = '.md'
    default_translator_class = MarkdownTranslator
    
    # current_docname = None
    # markdown_http_base = 'https://localhost'
    # imgpath: str = None
    supported_image_types = ['image/svg+xml', 'image/png',
                             'image/gif', 'image/jpeg']
    # search = True  # for things like HTML help and Apple help: suppress search
    # use_index = False
    md_documents =[]
        
    def init(self):
        # basename of images directory
        self.imagedir = '_images'
        # self.md_insert_html = self.get_conf('md_insert_html',True)
        self._doc_list = []
        
        self.md_insert_html = self.config.md_insert_html
        self.md_documents = self.config.md_documents
        
        # Get config values
        # self.md_insert_html = getattr(self.config, 'md_insert_html')
        # self.md_insert_html = self.get_builder_config('md_insert_html',True)
        

    def get_outdated_docs(self):
        # for docname in self.env.found_docs:
        #     if docname not in self.env.all_docs:
        #         yield docname
        #         continue
        #     targetname = path.join(self.outdir, docname + self.out_suffix)
        #     try:
        #         targetmtime = path.getmtime(targetname)
        #     except Exception:
        #         targetmtime = 0
        #     try:
        #         srcmtime = path.getmtime(self.env.doc2path(docname))
        #         if srcmtime > targetmtime:
        #             yield docname
        #     except EnvironmentError:
        #         pass
        return 'pass'
            
            
    def get_target_uri(self, docname: str, typ: str = None):
        if docname not in self.docnames:
            raise NoUri(docname, typ)
        else:
            return docname   + self.out_suffix
            
            
            
    def resolve_ref(self, tree, master):
        
        # self.get_doctree(master)
        
        TransClassList = self.app.registry.get_post_transforms()
        if ReferencesResolver in TransClassList:
            for i in range(len(TransClassList)):
                if TransClassList[i]  == ReferencesResolver:
                    TransClassList[i] =  ReferencesResolverNew
        
        self.env.resolve_references(tree, master, self)
        
                
    # def assemble_doctree(self, master, toctree_only):
    #     tree = self.env.get_doctree(master)
    #     if toctree_only:
    #         doc = new_document('mdbuilder/builder.py')
    #         for toctree in tree.traverse(addnodes.toctree):
    #             # ids is not assigned to toctree, but to the parent
    #             toctree.get('ids').extend(toctree.parent.get('ids'))
    #             doc.append(toctree)
    #         tree = doc
    #     tree = inline_all_toctrees(self, set(), master, tree, darkgreen, [master])    
    #     # tree = insert_all_toctrees(tree, self.env, [])
    #     tree['docname'] = master
    #     logger.info('')
    #     logger.info('resolving references...', nonl=True)
    #     print ("Apply post transforms ",self.app.registry.get_post_transforms())
    #     self.env.resolve_references(tree, master, self)
    #     # self.fix_refuris(tree)
    #     print("\n>>>> PRINT TOCTREE ",tree )
    
    #     # TODO: Support cross references
    #     return tree
    
    # def assemble_doctree(self, docname):
    #     print (">>>> ASEMBLE DOCTREE ", docname)
    #     tree = self.env.get_doctree(docname)
    #     tree = inline_all_toctrees(self, set(), docname, tree, darkgreen, [docname])
    #     tree['docname'] = docname
    #     print("self.md_documents ",self.md_documents )
    #     print (">>>> DOCTREE ", tree )
    #     print (">>>> DOCTREE ----------------------------------------------------------------")
    #     return tree

    
    def fix_refuris(self, tree: Node):
        # fix refuris with double anchor
        fname = self.config.root_doc + self.out_suffix
        for refnode in tree.traverse(nodes.reference):
            if 'refuri' not in refnode:
                continue
            refuri = refnode['refuri']
            hashindex = refuri.find('#')
            if hashindex < 0:
                continue
            hashindex = refuri.find('#', hashindex + 1)
            if hashindex >= 0:
                refnode['refuri'] = fname + refuri[hashindex:]        
            
            
    def assemble_doctree(self,master):
        #-> nodes.document:
        #
        # master = root_doc
        tree = self.env.get_doctree(master)
        tree = inline_all_toctrees(self, set(), master, tree, darkgreen, [master])
        
        tree['docname'] = master
        # self.env.resolve_references(tree, master, self)
        # self.resolve_ref(tree,master)
        TransClassList = self.app.registry.get_post_transforms()
        if ReferencesResolver in TransClassList:
            for i in range(len(TransClassList)):
                if TransClassList[i]  == ReferencesResolver:
                    TransClassList[i] =  ReferencesResolverNew
        
        self.env.resolve_references(tree, master, self) 
        self.fix_refuris(tree)
        print (">>>> ASSWMBLE DOCTREE ", tree )
        print (">>>> ASSWMBLE DOCTREE ----------------------------------------------------------------")
        return tree         
            
    def assemble_toc_secnumbers(self,master):
        # -> Dict[str, Dict[str, Tuple[int, ...]]]
        # Assemble toc_secnumbers to resolve section numbers on SingleHTML.
        # Merge all secnumbers to single secnumber.
        #
        # Note: current Sphinx has refid confliction in singlehtml mode.
        #       To avoid the problem, it replaces key of secnumbers to
        #       tuple of docname and refid.
        #
        #       There are related codes in inline_all_toctres() and
        #       HTMLTranslter#add_secnumber().
        new_secnumbers: Dict[str, Tuple[int, ...]] = {}
        for docname, secnums in self.env.toc_secnumbers.items():
            for id, secnum in secnums.items():
                alias = "%s/%s" % (docname, id)
                new_secnumbers[alias] = secnum

        print (">>>> assemble_toc_secnumbers ", new_secnumbers)
        return new_secnumbers
        # return {master: new_secnumbers}

    def assemble_toc_fignumbers(self,master) :
        #-> Dict[str, Dict[str, Dict[str, Tuple[int, ...]]]]
        # Assemble toc_fignumbers to resolve figure numbers on SingleHTML.
        # Merge all fignumbers to single fignumber.
        #
        # Note: current Sphinx has refid confliction in singlehtml mode.
        #       To avoid the problem, it replaces key of secnumbers to
        #       tuple of docname and refid.
        #
        #       There are related codes in inline_all_toctres() and
        #       HTMLTranslter#add_fignumber().
        print("ASSEMBLE TOC_FIGNUMBERS Source - self.env.toc_fignumbers",self.env.toc_fignumbers.items())
        
        new_fignumbers: Dict[str, Dict[str, Tuple[int, ...]]] = {}
        # {'foo': {'figure': {'id2': (2,), 'id1': (1,)}}, 'bar': {'figure': {'id1': (3,)}}}
        for docname, fignumlist in self.env.toc_fignumbers.items():
            for figtype, fignums in fignumlist.items():
                alias = "%s/%s" % (docname, figtype)
                new_fignumbers.setdefault(alias, {})
                for id, fignum in fignums.items():
                    new_fignumbers[alias][id] = fignum
                    
        print (">>>> assemble_toc_fignumbers ", new_fignumbers)
        return new_fignumbers
        # return {master: new_fignumbers}

            
            
    def write(self, *ignored):
        # docnames = self.env.all_docs   !!!!!!!!!

        for entry in self.md_documents:
            self.current_docname, out_docfile = entry[:2]
            toctree_only = entry[2] if len(entry) > 3 else False

            # logger.info('preparing documents... ', nonl=True)
            print('>>>> DOC LIST ',  self.current_docname)
            print('>>>> WRITE ------------------------------------------------------------------------------------ ')
            
            self.writer = MarkdownWriter(self)
            # self.prepare_writing(docnames)
            
            ###  Prepare fignumbers and sec_numbers for all documents.
            doctree = self.assemble_doctree(self.current_docname) 
            self.env.toc_secnumbers = self.assemble_toc_secnumbers(self.current_docname)
            self.env.toc_fignumbers = self.assemble_toc_fignumbers(self.current_docname)
            # logger.info('done')
            # print(">>>> ASSEMBLE toc_secnumbers  ", self.env.toc_secnumbers )
            # print(">>>> ASSEMBLE toc_fignumbers  ", self.env.toc_fignumbers )

            # logger.info('processing %s... ' % out_docfile, nonl=True)
            # doctree = self.assemble_doctree(start_doc, toctree_only)
            # doctree = self.assemble_doctree(self.current_docname)
            # logger.info('')
            
            # logger.info('writing... ', nonl=True)
            # logger.info('writing... ', start_doc)
            self.write_doc(self.current_docname, doctree, out_docfile)
            # logger.info('done') 
 
            
            
    # def prepare_writing(self, docnames):
        # for entry in self.config.md_documents:
        #     if entry[0] not in self.env.all_docs:
        #         logger.warning('unknown document %s is found ' 'in md_documents' % entry[0])
        #         continue
        #     if not entry[1]:
        #         logger.warning('invalid filename %s s found for %s ' 'in md_documents' % (entry[1]. entry[0]))
        #         continue
        #     self._doc_list.append(entry)
            
        # if not self._doc_list:
        #     logger.warning('no valid entry is found in md_documents')
        
            
    def write_doc(self, docname, doctree,out_docfile):
        # self.current_docname = docname
        
        self.resolve_ref(doctree, docname)
    
        outfilename = path.join(self.outdir, out_docfile)
        ensuredir(path.dirname(outfilename))
        destination = StringOutput(encoding='utf-8')
                
        # self.secnumbers = self.env.toc_secnumbers.get(docname, {})
        # self.fignumbers = self.env.toc_fignumbers.get(docname, {})
        
        self.secnumbers = self.env.toc_secnumbers
        self.fignumbers = self.env.toc_fignumbers

        # print(">>>> WRITE_DOC toc_secnumbers  ", self.secnumbers )
        # print(">>>> WRITE_DOC toc_fignumbers  ", self.fignumbers )        
    
        # print (">>>> WRITE_DOC PREPARE secnumbers source (self.env.toc_secnumbers)", self.env.toc_fignumbers)
        # print (">>>> WRITE_DOC PREPARE secnumbers", self.fignumbers)
        
        self.imgpath = relative_uri(docname, '_images')        
                
        self.writer.write(doctree, destination)        


        # outfilename = path.join(self.outdir,os_path(self.get_target_uri(docname)))
        # ensuredir(path.dirname(outfilename))
        
        try:
            with open(outfilename, 'w', encoding='utf-8') as f:  # type: ignore
                f.write(self.writer.output)
        except (IOError, OSError) as err:
            logger.warning(__('error writing file %s: %s'), outfilename, err)           
        
        # Accomulate and check document used images
        Builder.post_process_images(self, doctree)    
            
            
            
            
            
            
            
            
            
            
            
            
            



    # def get_target_uri(self, docname: str, typ: str = None) -> str:
    #     return quote(docname) + self.link_suffix










    # def prepare_writing(self, docnames):
    #     # create the search indexer
    #     # self.docnames
    #     self.indexer = None
    #     if self.search:
    #         from sphinx.search import IndexBuilder
    #         lang = self.config.html_search_language or self.config.language
    #         if not lang:
    #             lang = 'en'
    #         self.indexer = IndexBuilder(self.env, lang,
    #                                     self.config.html_search_options,
    #                                     self.config.html_search_scorer)

        
    #     self.writer = MarkdownWriter(self)
    #     # self.docsettings: Any = OptionParser(defaults=self.env.settings,components=(self.docwriter,),read_config_files=True).get_default_values()


    # def write_doc(self, docname, doctree):
    #     self.current_docname = docname
    #     self.secnumbers = self.env.toc_secnumbers.get(docname, {})
    #     self.fignumbers = self.env.toc_fignumbers.get(docname, {})
    #     print( ">>> WRITE_DOC docname=",docname,"\n    fignumbers=",self.fignumbers)
        
        
    #     destination = StringOutput(encoding='utf-8')
        
    #     self.writer.write(doctree, destination)
    #     outfilename = path.join(self.outdir,os_path(docname) + self.out_suffix)
    #     ensuredir(path.dirname(outfilename))
        
    #     try:
    #         with open(outfilename, 'w', encoding='utf-8') as f:  # type: ignore
    #             f.write(self.writer.output)
    #     except (IOError, OSError) as err:
    #         logger.warning(__('error writing file %s: %s'), outfilename, err)
            
            
    # def write_doc_serialized(self, docname: str, doctree: nodes.document):
    #     self.imgpath = relative_uri(self.get_target_uri(docname), self.imagedir)
    #     self.post_process_images(doctree)
        
        
    # def post_process_images(self, doctree: Node):
    #     if      
        

    def copy_image_files(self):
        if self.images:
            stringify_func = ImageAdapter(self.app.env).get_original_image_uri
            ensuredir(path.join(self.outdir, self.imagedir))
            for src in status_iterator(self.images, __('copying images... '), "brown",
                                       len(self.images), self.app.verbosity,
                                       stringify_func=stringify_func):
                dest = self.images[src]
                try:
                    copyfile(path.join(self.srcdir, src),
                             path.join(self.outdir, self.imagedir, dest))
                except Exception as err:
                    logger.warning(__('cannot copy image file %r: %s'),
                                   path.join(self.srcdir, src), err)


    # def finish(self):
    def finish(self):
        self.finish_tasks.add_task(self.copy_image_files)



### ?????
def insert_all_toctrees(tree, env, traversed):
    tree = tree.deepcopy()
    for toctreenode in tree.traverse(addnodes.toctree):
        nodeid = 'docx_expanded_toctree%d' % id(toctreenode)
        newnodes = nodes.container(ids=[nodeid])
        toctreenode['docx_expanded_toctree_refid'] = nodeid
        includefiles = toctreenode['includefiles']
        for includefile in includefiles:
            if includefile in traversed:
                continue
            try:
                traversed.append(includefile)
                subtree = insert_all_toctrees(
                        env.get_doctree(includefile), env, traversed)
            except Exception:
                continue
            start_of_file = addnodes.start_of_file(docname=includefile)
            start_of_file.children = subtree.children
            newnodes.append(start_of_file)
        parent = toctreenode.parent
        index = parent.index(toctreenode)
        parent.insert(index + 1, newnodes)
    return tree



##############################################################################################


from sphinx.domains.std import StandardDomain
from docutils.nodes import Element
from sphinx.application import Sphinx
from sphinx.builders import Builder
from sphinx.environment import BuildEnvironment
from sphinx.addnodes import desc_signature, pending_xref
from typing import (Any, Callable, Dict, Iterable, Iterator, List, Optional,  Tuple, Type, Union, cast)

# class StandardDomainNew(StandardDomain):



def resolve_xref_new(self, env: "BuildEnvironment", fromdocname: str, builder: "Builder",
                typ: str, target: str, node: pending_xref, contnode: Element ):


    # print (">>>> resolve_xref_new",
    #     "\n    env= ",env,
    #     "\n    fromdocname= ",fromdocname,
    #     "\n    builder=",builder,
    #     "\n    typ=",typ,
    #     "\n    target=",target,
    #     "\n    node=",node,
    #     "\n    contnode=",contnode
    #     )


    if typ == 'ref':
        resolver = self._resolve_ref_xref
    elif typ == 'numref':
        resolver = self._resolve_numref_xref
    elif typ == 'keyword':
        resolver = self._resolve_keyword_xref
    elif typ == 'doc':
        resolver = self._resolve_doc_xref
    elif typ == 'option':
        resolver = self._resolve_option_xref
    elif typ == 'term':
        resolver = self._resolve_term_xref
    else:
        resolver = self._resolve_obj_xref


    return resolver(self, env, fromdocname, builder, typ, target, node, contnode)



def _resolve_numref_xref_new(self, 
                        env: "BuildEnvironment", 
                        fromdocname: str,
                        builder: "Builder", 
                        typ: str, 
                        target: str,
                        node: pending_xref, 
                        contnode: Element):

    if target in self.labels:
        docname, labelid, figname = self.labels.get(target, ('', '', ''))
    else:
        docname, labelid = self.anonlabels.get(target, ('', ''))
        figname = None


    print (">>>> _resolve_numref_xref_new",
            "\n    labels= ",self.labels,
            "\n    typ=",typ,
            "\n    fromdocname=",fromdocname,
            "\n    body=",docname,
            )

    if not docname:
        return None

    target_node = env.get_doctree(docname).ids.get(labelid)
    figtype = self.get_enumerable_node_type(target_node)
    if figtype is None:
        return None

    if figtype != 'section' and env.config.numfig is False:
        logger.warning(__('numfig is disabled. :numref: is ignored.'), location=node)
        return contnode

    try:
        
        
        print (">>>> _resolve_numref_xref_new",
            "\n    env= ",env,
            "\n    builder= ",builder,
            "\n    figtype=",figtype,
            "\n    docname=",docname,
            "\n    target_node=",target_node
            )
        
        
        # fignumber = self.get_fignumber(env, builder, figtype, docname, target_node)
        
        
        figure_id = target_node['ids'][0]
        fignumber = 'undef'
        
        print (">>>> _resolve_numref_xref_new",
            "\n    -----------",              
            "\n    env.toc_fignumbers=",env.toc_fignumbers,
            "\n    figure_id=",figure_id,
            "\n    fignumber=",fignumber
            )
                
                
        #  from self.get_fignumber(env, builder, figtype, docname, target_node)        
        a = env.toc_fignumbers[docname]
        
        b = a[figtype]           
        
        fignumber = b[figure_id]
        
        
        if fignumber is None:
            return contnode
    except ValueError:
        logger.warning(__("Failed to create a cross reference. Any number is not "
                            "assigned: %s"),
                        labelid, location=node)
        return contnode

    try:
        if node['refexplicit']:
            title = contnode.astext()
        else:
            title = env.config.numfig_format.get(figtype, '')

        if figname is None and '{name}' in title:
            logger.warning(__('the link has no caption: %s'), title, location=node)
            return contnode
        else:
            fignum = '.'.join(map(str, fignumber))
            if '{name}' in title or 'number' in title:
                # new style format (cf. "Fig.{number}")
                if figname:
                    newtitle = title.format(name=figname, number=fignum)
                else:
                    newtitle = title.format(number=fignum)
            else:
                # old style format (cf. "Fig.%s")
                newtitle = title % fignum
    except KeyError as exc:
        logger.warning(__('invalid numfig_format: %s (%r)'), title, exc, location=node)
        return contnode
    except TypeError:
        logger.warning(__('invalid numfig_format: %s'), title, location=node)
        return contnode

    return self.build_reference_node(fromdocname, builder,
                                        docname, labelid, newtitle, 'numref',
                                        nodeclass=addnodes.number_reference,
                                        title=title)



##############################################################################################
###
###   For testing
###
from sphinx.addnodes import pending_xref
from sphinx.util.nodes import find_pending_xref_condition, process_only_nodes

class ReferencesResolverNew(ReferencesResolver):

    default_priority=9

    def find_pending_xref_condition(self, node: pending_xref, conditions: Sequence[str]):
        for condition in conditions:
            matched = find_pending_xref_condition(node, condition)
            if matched:
                return matched.children
        else:
            return None

    
    
    def run(self, **kwargs: Any):
        for node in self.document.traverse(addnodes.pending_xref):
            content = self.find_pending_xref_condition(node, ("resolved", "*"))

            if content:
                contnode = cast(Element, content[0].deepcopy())
            else:
                contnode = cast(Element, node[0].deepcopy())

            print(">>>> RUN, content=",contnode,"\nnode=",node)

            newnode = None

            typ = node['reftype']
            target = node['reftarget']
            refdoc = node.get('refdoc', self.env.docname)
            domain = None

            try:
                if 'refdomain' in node and node['refdomain']:
                    # let the domain try to resolve the reference
                    try:
                        domain = self.env.domains[node['refdomain']]
                    except KeyError as exc:
                        raise NoUri(target, typ) from exc
                    
                    
                    ###
                    ###   Need change
                    ###
                    print (">>>> RUN",
                        "\n    typ= ",typ,
                        "\n    target= ",target,
                        "\n    refdoc=",refdoc,
                        "\n    contnode=",contnode
                        )
                    
                    setattr(domain, '_resolve_numref_xref', _resolve_numref_xref_new)  
                    setattr(domain, 'resolve_xref', resolve_xref_new) 
                    
                    newnode = domain.resolve_xref(domain, self.env, refdoc, self.app.builder, typ, target, node, contnode)
                # really hardwired reference types
                elif typ == 'any':
                    newnode = self.resolve_anyref(refdoc, node, contnode)
                # no new node found? try the missing-reference event
                if newnode is None:
                    newnode = self.app.emit_firstresult('missing-reference', self.env,
                                                        node, contnode,
                                                        allowed_exceptions=(NoUri,))
                    # still not found? warn if node wishes to be warned about or
                    # we are in nit-picky mode
                    if newnode is None:
                        self.warn_missing_reference(refdoc, typ, target, node, domain)
            except NoUri:
                newnode = None

            if newnode:
                newnodes: List[Node] = [newnode]
            else:
                newnodes = [contnode]
                if newnode is None and isinstance(node[0], addnodes.pending_xref_condition):
                    matched = self.find_pending_xref_condition(node, ("*",))
                    if matched:
                        newnodes = matched
                    else:
                        logger.warning(__('Could not determine the fallback text for the '
                                          'cross-reference. Might be a bug.'), location=node)

            node.replace_self(newnodes)







