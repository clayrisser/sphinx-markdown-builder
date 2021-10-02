from .markdown_writer import MarkdownWriter, MarkdownTranslator
from docutils.io import StringOutput
from docutils import nodes
from docutils.frontend import OptionParser
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

logger = logging.getLogger(__name__)

class MarkdownBuilder(Builder):
    name = 'markdown'
    format = 'markdown'
    epilog = __('The markdown files are in %(outdir)s.')
    out_suffix = '.md'
    allow_parallel = True
    default_translator_class = MarkdownTranslator
    current_docname = None
    markdown_http_base = 'https://localhost'
    imgpath: str = None
    supported_image_types = ['image/svg+xml', 'image/png',
                             'image/gif', 'image/jpeg']
    search = True  # for things like HTML help and Apple help: suppress search
    use_index = False

    def init(self):
        self.secnumbers = {}
        # basename of images directory
        self.imagedir = '_images'
        

    def get_outdated_docs(self):
        for docname in self.env.found_docs:
            if docname not in self.env.all_docs:
                yield docname
                continue
            targetname = path.join(self.outdir, docname + self.out_suffix)
            try:
                targetmtime = path.getmtime(targetname)
            except Exception:
                targetmtime = 0
            try:
                srcmtime = path.getmtime(self.env.doc2path(docname))
                if srcmtime > targetmtime:
                    yield docname
            except EnvironmentError:
                pass

    def get_target_uri(self, docname: str, typ=None):
        # Returns the target markdown file name
        return f"{docname}.md"

    # def get_target_uri(self, docname: str, typ: str = None) -> str:
    #     return quote(docname) + self.link_suffix



    def prepare_writing(self, docnames):
        # create the search indexer
        self.indexer = None
        if self.search:
            from sphinx.search import IndexBuilder
            lang = self.config.html_search_language or self.config.language
            if not lang:
                lang = 'en'
            self.indexer = IndexBuilder(self.env, lang,
                                        self.config.html_search_options,
                                        self.config.html_search_scorer)

        
        self.writer = MarkdownWriter(self)
        # self.docsettings: Any = OptionParser(defaults=self.env.settings,components=(self.docwriter,),read_config_files=True).get_default_values()


    def write_doc(self, docname, doctree):
        self.current_docname = docname
        self.secnumbers = self.env.toc_secnumbers.get(docname, {})
        self.fignumbers = self.env.toc_fignumbers.get(docname, {})
        destination = StringOutput(encoding='utf-8')
        
        self.writer.write(doctree, destination)
        outfilename = path.join(self.outdir,os_path(docname) + self.out_suffix)
        ensuredir(path.dirname(outfilename))
        
        try:
            with open(outfilename, 'w', encoding='utf-8') as f:  # type: ignore
                f.write(self.writer.output)
        except (IOError, OSError) as err:
            logger.warning(__('error writing file %s: %s'), outfilename, err)
            
            
    def write_doc_serialized(self, docname: str, doctree: nodes.document):
        self.imgpath = relative_uri(self.get_target_uri(docname), self.imagedir)
        self.post_process_images(doctree)
        

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


def setup(app: Sphinx) -> Dict[str, Any]:
    app.add_builder(MarkdownBuilder)
    app.setup_extension('sphinx.builders.md')

    return {
        'version': 'builtin',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }