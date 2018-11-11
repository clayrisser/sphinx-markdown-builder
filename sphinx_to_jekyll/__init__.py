from .jekyll_builder import JekyllBuilder

def setup(app):
    app.add_builder(JekyllBuilder)
