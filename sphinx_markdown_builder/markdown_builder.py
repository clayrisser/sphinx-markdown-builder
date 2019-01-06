from .markdown_writer import MarkdownWriter, MarkdownTranslator
from docutils.io import StringOutput
from io import open
from os import path
from sphinx.builders import Builder
from sphinx.builders import Builder
from sphinx.locale import __
from sphinx.util import logging
from sphinx.util.osutil import ensuredir, os_path
import shutil
import os


if False:
    from typing import Any, Dict, Iterator, Set, Tuple
    from docutils import nodes
    from sphinx.application import Sphinx

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

    def init(self):
        self.secnumbers = {}

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

    def get_target_uri(self, docname, typ=None):
        return ''

    def prepare_writing(self, docnames):

        # copy dependencies (images, references files)
        print "copying dependencies..."
        for (doc, deps) in self.env.dependencies.iteritems():
            for dep in deps:
                source = os.path.abspath(os.path.join(self.srcdir, dep))
                target = os.path.abspath(os.path.join(self.outdir, dep))
                target_dir = os.path.dirname(target)

                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)

                if not os.path.exists(source):
                    print "warning: cannot find resource %s referenced from %s" % (dep, doc)
                else:
                    if not os.path.exists(target):
                        shutil.copy(source, target)

        # calculate parents and grandparents
        self.parents = {}
        self.grandparents = {}

        # figure out parents
        for (parent, children) in self.env.toctree_includes.iteritems():
            for child in children:
                self.parents[child] = parent

        # figure out grandparents
        for (docname, parent) in self.parents.iteritems():
            self.grandparents[docname] = self.parents.get(parent)

        self.writer = MarkdownWriter(self)

    def write_doc(self, docname, doctree):
        self.current_docname = docname
        self.secnumbers = self.env.toc_secnumbers.get(docname, {})
        destination = StringOutput(encoding='utf-8')
        self.writer.write(doctree, destination)
        outfilename = path.join(self.outdir, os_path(docname) + self.out_suffix)
        ensuredir(path.dirname(outfilename))
        try:
            with open(outfilename, 'w', encoding='utf-8') as f:  # type: ignore
                f.write(self.writer.output)
        except (IOError, OSError) as err:
            logger.warning(__("error writing file %s: %s"), outfilename, err)

    def finish(self):
        pass
