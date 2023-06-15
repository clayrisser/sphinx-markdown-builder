from .markdown_builder import MarkdownBuilder


def setup(app):
    app.add_builder(MarkdownBuilder)
    app.add_config_value("markdown_http_base", "", False)
    app.add_config_value("markdown_uri_doc_suffix", ".md", False)
