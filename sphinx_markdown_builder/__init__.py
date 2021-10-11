from .markdown_builder import MarkdownBuilder
from sphinx.util.osutil import make_filename


from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.util import DownloadFiles, FilenameUniqDict, logging
from typing import (TYPE_CHECKING, Any, Callable, Dict, Generator, Iterator, List, Optional,
                    Set, Tuple, Union)

# logger = logging.getLogger(__name__)

# def check_doclist(app: "Sphinx", env: "BuildEnvironment", added: Set[str],
#                    changed: Set[str], removed: Set[str]):
    
#     if env.config.md_singledoc:
        
#         print(">>>> check_doclist env.all_docs=", env.all_docs)
#         print(">>>> check_doclist env.found_docs=", env.found_docs)
        
#         added =[]
#         changed = []
#         removed = []
        
#         for entry in env.config.md_documents:
#             current_docname, out_docfile = entry[:2]
#             for doc in env.found_docs:
#                 if doc != current_docname:
#                     removed.append(doc)
        
        
        
#         if added:
#             for the_doc in added:
#                 print ("check_doclist ADD=",the_doc)

#         if changed:
#             for the_doc in changed:
#                 print ("check_doclist CHANGE=",the_doc)

#         if removed:
#             for the_doc in removed:
#                 print ("check_doclist REMOVE=",the_doc)


#     return removed





def setup(app):
    app.add_builder(MarkdownBuilder)
    def default_md_documents(conf):
        start_doc = conf.master_doc
        filename = '%s.md' % make_filename(conf.project)
        toc_only = True
        return [(start_doc, filename, toc_only)]
    
    #  Register event callback befor read and add to catalog
    # app.connect('env-get-outdated', check_doclist)
    
    app.add_config_value('md_documents', default_md_documents, 'env') 
    app.add_config_value('md_insert_html', True, 'env') 
    app.add_config_value('md_singledoc', True, 'env')   
    