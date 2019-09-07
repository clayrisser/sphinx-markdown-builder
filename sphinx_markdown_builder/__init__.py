from .markdown_builder import MarkdownBuilder

def setup(app):
    app.add_builder(MarkdownBuilder)
