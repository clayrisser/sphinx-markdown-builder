from codecs import open
from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

install_requires = list()
with open(path.join(here, 'requirements.txt'), 'r', encoding='utf-8') as f:
    for line in f.readlines():
        install_requires.append(line.split('=')[0].strip('<~>'))

setup(
    name='sphinx-markdown-builder',
    version='0.5.5',
    description='sphinx builder that outputs markdown files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/WeiChe-Huang/sphinx-markdown-builder',
    author='Andy Huang',
    author_email='andy.huang@kneron.us',
    license='MIT',

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='sphinx docs documentation markdown',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=install_requires,
    include_package_data=True,
    entry_points={
        'sphinx.builders': [
            'markdown = sphinx_markdown_builder',
        ],
    }
)
