from .markdown_builder import MarkdownBuilder
from sphinx.util.osutil import make_filename

def setup(app):
    app.add_builder(MarkdownBuilder)
    def default_md_documents(conf):
        start_doc = conf.master_doc
        filename = '%s.md' % make_filename(conf.project)
        toc_only = True
        return [(start_doc, filename, toc_only)]
    
    app.add_config_value('md_documents', default_md_documents, 'env') 
    app.add_config_value('md_insert_html', True, 'env')   
    