""" Testing """
# flake8: noqa
import sys
import os
try:
    import rydown
except Exception as e:
    sys.path.append(os.path.abspath('.'))
    sys.path.append('/'.join([os.path.abspath('.'), 'rydown']))
    import rydown
import rydown.lexer as lexer
import rydown.parser as parser
import rydown.serializer as serializer


def test_heading_h1_underline():
    """Underline header level 1"""
    resp = rydown.to_mediawiki("Heading 1\n=========\n")
    assert resp == "= Heading 1 =\n"


def test_heading_h1_underline_singleline():
    resp = rydown.to_mediawiki("Heading 1\n=========\nOnly one newline\n")
    assert resp == "= Heading 1 =\n<p>Only one newline</p>\n"


def test_heading_h2_underline():
    """Underline header level 2"""
    resp = rydown.to_mediawiki("Heading 2\n---------\n")
    assert resp == "== Heading 2 ==\n"


def test_heading_h1():
    """Header level 1"""
    resp = rydown.to_mediawiki("# Heading 1\n")
    assert resp == "= Heading 1 =\n"


def test_heading_h2():
    """Header level 2"""
    resp = rydown.to_mediawiki("## Heading 2\n")
    assert resp == "== Heading 2 ==\n"


def test_heading_h3_a():
    """Header level 3"""
    resp = rydown.to_mediawiki("### Heading 3\n")
    assert resp == "=== Heading 3 ===\n"


def test_heading_h3_b():
    """Header level 3"""
    resp = rydown.to_mediawiki("### Heading 3 ###\n\n")
    assert resp == "=== Heading 3 ===\n"


def test_paragraph():
    resp = rydown.to_mediawiki("Paragraphs are separated\nby a blank line.\n")
    assert resp == "<p>Paragraphs are separated\nby a blank line.</p>\n"


def test_textitalic_asterisc():
    resp = rydown.to_mediawiki("*italic*\n")
    assert resp == "<p>'' italic ''</p>\n" or resp == "<p>''italic''</p>\n"


def test_textbold_asterisc():
    resp = rydown.to_mediawiki("**bold**\n")
    assert resp == "<p>'''bold'''</p>\n" or resp == "<p>''' bold '''</p>\n"


def test_textitalicbold_asterisc():
    resp = rydown.to_mediawiki("***italic bold***\n")
    assert resp == "<p>'''''italic bold'''''</p>\n" or resp == "<p>''''' italic bold '''''</p>\n"


def test_table():
    resp = rydown.to_mediawiki("a|b|c\n-|-|-\nd|e|f\n\n")
    assert resp == "\n{|\n!a\n!b\n!c\n|-\n|d\n|e\n|f\n|}\n"


def test_textattributes():
    resp = rydown.to_mediawiki(
        "Text attributes _italic_, **bold**, `monospace`.\n")
    assert resp == "<p>Text attributes _italic_, '''bold''',"\
        " <code>monospace</code>.</p>\n"


def test_bulletlist_asterisc():
    resp = rydown.to_mediawiki("* apples\n* oranges\n* pears\n\n")
    assert resp == "*apples\n*oranges\n*pears\n"


def test_bulletlist_plus():
    resp = rydown.to_mediawiki("+ apples\n+ oranges\n+ pears\n\n")
    assert resp == "*apples\n*oranges\n*pears\n"


def test_bulletlist_minus():
    resp = rydown.to_mediawiki("- apples\n- oranges\n- pears\n\n")
    assert resp == "*apples\n*oranges\n*pears\n"


def test_bulletlist_asterisc_sublists_spaces():
    resp = rydown.to_mediawiki("* apples\n  * oranges\n    * pears\n      * bananas\n        * tomatos\n\n")
    assert resp == "*apples\n**oranges\n***pears\n****bananas\n*****tomatos\n"


def test_bulletlist_asterisc_sublists_tabs():
    resp = rydown.to_mediawiki("* apples\n\t* oranges\n\t\t* pears\n\t\t\t* bananas\n\t\t\t\t* tomatos\n\n")
    assert resp == "*apples\n**oranges\n***pears\n****bananas\n*****tomatos\n"


def test_numberedlist():
    resp = rydown.to_mediawiki("1. apples\n2. oranges\n3. pears\n\n")
    assert resp == """<ol>
<li>apples</li>
<li>oranges</li>
<li>pears</li>
</ol>\n"""


def test_numberedlist_mixnumering():
    resp = rydown.to_mediawiki("2. apples\n3. oranges\n1. pears\n\n")
    assert resp == """<ol>
<li>apples</li>
<li>oranges</li>
<li>pears</li>
</ol>\n"""


def test_comment_simple():
    resp = rydown.to_mediawiki("<-- Comment -->")
    assert resp == ""


def test_comment_startline():
    resp = rydown.to_mediawiki("<-- Comment -->Comment in the beginning of line\n")
    assert resp == "<p>Comment in the beginning of line</p>\n"


def test_link():
    resp = rydown.to_mediawiki("A [link](https://www.example.com).\n")
    assert resp == "<p>A [https://www.example.com link].</p>\n"


def test_link_ref():
    resp = rydown.to_mediawiki("""[an example][id]\n\n[id]: http://example.com/\n""")
    assert resp == "<p>[http://example.com/#id an example]</p>\n"


def test_image():
    resp = rydown.to_mediawiki("![Image](https://www.example.com/img.png)\n")
    assert resp == """<span class="plainlinks">[{{fullurl:Image}} https://www.example.com/img.png]</span>"""


def test_blockquote():
    resp = rydown.to_mediawiki(
        "> Markdown uses email-style > characters for blockquoting.\n\n")
    assert resp == "<blockquote><p> Markdown uses email-style &gt;" \
        " characters for blockquoting.</p></blockquote>\n"


def test_blockquote_two_paragraphs():
    resp = rydown.to_mediawiki("""> This is a blockquote with two paragraphs.
> Lorem ipsum dolor sit amet,
> consectetuer adipiscing elit. Aliquam hendrerit mi posuere lectus.
> Vestibulum enim wisi, viverra nec, fringilla in, laoreet vitae, risus.
>
> Donec sit amet nisl. Aliquam semper ipsum sit amet velit. Suspendisse
> id sem consectetuer libero luctus adipiscing.\n\n""")
    assert resp == """<blockquote><p> This is a blockquote with two paragraphs.
 Lorem ipsum dolor sit amet,
 consectetuer adipiscing elit. Aliquam hendrerit mi posuere lectus.
 Vestibulum enim wisi, viverra nec, fringilla in, laoreet vitae, risus.
 
 Donec sit amet nisl. Aliquam semper ipsum sit amet velit. Suspendisse
 id sem consectetuer libero luctus adipiscing.</p></blockquote>\n"""


def test_blockquote_two_blockquotes():
    resp = rydown.to_mediawiki("""> This is a blockquote with two paragraphs.
Lorem ipsum dolor sit amet,
consectetuer adipiscing elit. Aliquam hendrerit mi posuere lectus.
Vestibulum enim wisi, viverra nec, fringilla in,
laoreet vitae, risus.

> Donec sit amet nisl. Aliquam semper ipsum sit amet velit.
Suspendisse id sem consectetuer libero
luctus adipiscing.\n\n""")
    assert resp == """<blockquote><p> This is a blockquote with two paragraphs.
Lorem ipsum dolor sit amet,
consectetuer adipiscing elit. Aliquam hendrerit mi posuere lectus.
Vestibulum enim wisi, viverra nec, fringilla in,
laoreet vitae, risus.</p></blockquote>
<blockquote><p> Donec sit amet nisl. Aliquam semper ipsum sit amet velit.
Suspendisse id sem consectetuer libero
luctus adipiscing.</p></blockquote>\n"""


def test_inlinecode():
    resp = rydown.to_mediawiki("`This is a code block.`\n")
    assert resp == "<p><code>This is a code block.</code></p>\n"


def test_codeblock_nolang():
    resp = rydown.to_mediawiki("""```
This is a code block.```\n""")
    assert resp == "<syntaxhighlight lang='text'>This is a" \
        " code block.</syntaxhighlight>\n"


def test_codeblock_lang():
    resp = rydown.to_mediawiki("""```bash
This is a code block.```\n""")
    assert resp == "<syntaxhighlight lang='bash'>This is a" \
        " code block.</syntaxhighlight>\n"


def test_not_numberedlist():
    resp = rydown.to_mediawiki("1986\. What a great season.\n")
    assert resp == "<p>1986. What a great season.</p>\n"
