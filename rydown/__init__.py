import parser
import serializer
from ._version import get_versions


def to_html(markdownContent):
    p = parser.MarkdownParser()
    tree = p.parse(markdownContent)
    htmlContent = serializer.serialize(tree)
    return htmlContent


def to_mediawiki(markdownContent):
    p = parser.MarkdownParser()
    tree = p.parse(markdownContent)
    mediawikiContent = serializer.mediawiki_serialize(tree)
    return mediawikiContent


__version__ = get_versions()['version']
del get_versions
