
import re

from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments import highlight

from codesyntax.RysObjectiveCLexer import RysObjectiveCLexer
from codesyntax.RysGitLexer import RysGitLexer
from codesyntax.RysGitOutputLexer import RysGitOutputLexer


def serialize(node):
    return r_node(node)


def mediawiki_serialize(node):
    return r_wiki_node(node)


def r_node(node):
    node_type = node[0]
    out = ""
    if node_type == 'document':
        for block in node[1]:
            out += r_node(block)

    elif node_type == 'heading':
        out += "<h%s>" % node[2]
        for phrase in node[1]:
            out += r_node(phrase)
        out += "</h%s>" % node[2]

    elif node_type == 'subheading':
        a = node[1].pop()
        out += "<h1>%s</h1>" % a[1]

    elif node_type == 'paragraph':
        out += "<p>"
        for phrase in node[1]:
            out += r_node(phrase)
        out += "</p>"

    elif node_type == 'emphasisstrong':
        out += "<em><strong>"
        for phrase in node[1]:
            out += r_node(phrase)
        out += "</strong></em>"

    elif node_type == 'emphasis':
        out += "<em>"
        for phrase in node[1]:
            out += r_node(phrase)
        out += "</em>"

    elif node_type == 'strong':
        out += "<strong>"
        for phrase in node[1]:
            out += r_node(phrase)
        out += "</strong>"

    elif node_type == 'inline_code':
        # Only replace HTML special chars, not dashes like in text nodes
        value = node[1]
        value = value.replace('&', '&amp;')
        value = value.replace('<', '&lt;')
        value = value.replace('>', '&gt;')
        out += "<code>%s</code>" % value

    elif node_type == 'link':
        out += "<a href='%s'>" % node[2]
        for phrase in node[1]:
            out += r_node(phrase)
        out += "</a>"

    elif node_type == 'ref_link':
        # Key is in node[2] if you want to display traditional footnotes
        out += "<a href='%s'>" % node[3]
        for phrase in node[1]:
            out += r_node(phrase)
        out += "</a>"

    elif node_type == 'figure':
        out += "<figure><img src='%s' /><figcaption>" % node[2]
        for phrase in node[1]:
            out += r_node(phrase)
        out += "</figcaption></figure>"

    elif node_type == 'ulist':
        out += "<ul>"
        for item in node[1]:
            out += r_node(item)
        out += "</ul>"

    elif node_type == 'olist':
        out += "<ol>"
        for item in node[1]:
            out += r_node(item)
        out += "</ol>"

    elif node_type == 'list_item':
        out += "<li>"
        for phrase_or_list in node[1]:
            out += r_node(phrase_or_list)
        out += "</li>"

    elif node_type == 'blocker_code':
        language = node[2]
        if language == '':
            language = 'text'
        out += "<code language='{}'>".format(language)
        for phrase_or_list in node[1]:
            out += r_node(phrase_or_list)
        out += "</code>"

    elif node_type == 'block_code':
        language = node[2]
        if node[2] == '':
            language = 'text'

        # Convert tabs to spaces
        content = re.sub(r'\t', '    ', node[1])
        # Use Pygments to highlight the code block
        formatter = HtmlFormatter(encoding='utf-8')
        rendered = highlight(content, get_lexer(language), formatter)
        rendered = rendered.replace('<div class="highlight"><pre>', '<pre>')
        rendered = rendered.replace('</pre></div>', '</pre>')
        rendered = rendered.replace('<span', '<code')
        rendered = rendered.replace('</span>', '</code>')
        out += rendered

    elif node_type == 'text':
        value = node[1].replace('\n', ' ')
        # Replace HTML entities (order matters!)
        value = re.sub(r"&(?!(\w|#)\w+;)", "&amp;", value)
        value = value.replace('---', '&mdash;')
        value = value.replace('--', '&ndash;')
        value = value.replace('<', '&lt;')
        value = value.replace('>', '&gt;')

        # --- Replace straight quotes with curly quotes (order matters!) ---
        # General rule: if it's touching a non-space/non-quote,turn it that way

        # Minor hack for avoiding start/end pattern mating
        value = " " + value + " "

        # Double quote edge cases
        value = re.sub(r"(?<![ ])\"'", "&rdquo;&rsquo;", value)
        value = re.sub(r"\"'(?![ ])", "&ldquo;&lsquo;", value)
        value = re.sub(r"(?<![ ])'\"", "&rsquo;&rdquo;", value)
        value = re.sub(r"'\"(?![ ])", "&lsquo;&ldquo;", value)

        # Single quotes (turn right first for apostrophes
        value = re.sub(r"(?<![ ])'", "&rsquo;", value)
        value = re.sub(r"'(?![ ])", "&lsquo;", value)

        # Double quotes
        value = re.sub(r"(?<![ ])\"", "&rdquo;", value)
        value = re.sub(r"\"(?![ ])", "&ldquo;", value)

        # Remove minor hack
        value = value[1:-1]

        out += value

    return out


def r_wiki_node(node):
    node_type = node[0]
    out = ""
    if node_type == 'document':
        for block in node[1]:
            out += r_wiki_node(block)

    elif node_type == 'heading':
        out += "=" * int(node[2]) + " "
        for phrase in node[1]:
            out += r_wiki_node(phrase)
        out += " " + "=" * int(node[2]) + '\n'

    elif node_type == 'subheading':
        a = node[1].pop()
        out += "= %s =\n" % a[1]

    elif node_type == 'horizontalline':
        out += "----\n"

    elif node_type == 'blockquote':
        text = ''
        for phrase in node[1]:
            text += r_wiki_node(phrase)
        out += "<blockquote><p>{}</p></blockquote>\n".format(text)

    elif node_type == 'paragraph':
        out += "<p>"
        for phrase in node[1]:
            out += r_wiki_node(phrase)
        out += "</p>\n"

    elif node_type == 'emphasisstrong':
        out += "''''' " + node[1] + " '''''"

    elif node_type == 'emphasis':
        out += "'' " + node[1] + " ''"

    elif node_type == 'strong':
        out += "''' " + node[1] + " '''"

    elif node_type == 'inline_code':
        # Only replace HTML special chars, not dashes like in text nodes
        value = node[1]
        value = value.replace('&', '&amp;')
        value = value.replace('<', '&lt;')
        value = value.replace('>', '&gt;')
        out += "<code>%s</code>" % value

    elif node_type == 'link':
        text = ''
        for phrase in node[1]:
            text += r_wiki_node(phrase)
        out += "[{} {}]".format(node[2], text)

    elif node_type == 'ref_link':
        # Key is in node[2] if you want to display traditional footnotes
        text = ''
        for phrase in node[1]:
            text += r_node(phrase)
        url = node[3].split(' ')[0]
        out += "[{}#{} {}]".format(url, node[2], text)

    elif node_type == 'figure':
        text = ''
        for phrase in node[1]:
            text += r_wiki_node(phrase)
        out += ("<span class=\"plainlinks\">"
                "[{{{{fullurl:{}}}}} {}]</span>".format(text, node[2]))

    elif node_type == 'table_head':
        out += "\n{|\n"
        out += '!' + node[1].replace('|', '\n!')
        if len(node) == 3:
            out += '\n|-\n'
            out += r_wiki_node(node[2])
        # int(k[1:k.find('}')])
        out += "\n|}\n"

    elif node_type == 'table_body':
        out += '|' + node[1].replace('|', '\n|')
        if len(node) == 3:
            out += '\n|-\n'
            out += r_wiki_node(node[2])

    elif node_type == 'ulist':
        for item in node[1]:
            out += r_wiki_node(item)

    elif node_type == 'olist':
        out += "<ol>\n"
        for item in node[1]:
            out += r_wiki_node(item)
        out += "</ol>\n"

    elif node_type == 'list_uitem':
        identation = '*' * int(node[1][-1])
        phrase_or_list = ['phrase_list', node[1]]
        out += '*' + identation
        for phrase_or_list in node[1]:
            out += r_wiki_node(phrase_or_list).strip()
        out += "\n"

    elif node_type == 'list_item':
        out += '<li>'
        for phrase_or_list in node[1]:
            out += r_wiki_node(phrase_or_list).strip()
        out += "</li>\n"

    elif node_type == 'blocker_code':
        language = node[2]
        if node[2] == '':
            language = 'text'
        out += ("<syntaxhighlight lang='{}'>"
                "{}</syntaxhighlight>\n".format(language, node[1]))

    elif node_type == 'block_code':
        language = node[2]
        if node[2] == '':
            language = 'text'
        # Convert tabs to spaces
        content = re.sub(r'\t', '    ', node[1])
        # Use Pygments to highlight the code block
        formatter = HtmlFormatter(encoding='utf-8')
        rendered = highlight(content, get_lexer(language), formatter)
        rendered = rendered.replace('<div class="highlight"><pre>', '<pre>')
        rendered = rendered.replace('</pre></div>', '</pre>')
        rendered = rendered.replace('<span>', '')
        rendered = rendered.replace('</span>', '')
        out += rendered

    elif node_type == 'text':
        value = node[1].replace('\n', '/n')
        # Replace HTML entities (order matters!)
        value = re.sub(r"&(?!(\w|#)\w+;)", "&amp;", value)
        value = value.replace('<', '&lt;')
        value = value.replace('>', '&gt;')

        # --- Replace straight quotes with curly quotes (order matters!) ---
        # General rule: if it's touching a non-space/non-quote,turn it that way

        # Minor hack for avoiding start/end pattern mating
        value = " " + value + " "

        # Double quote edge cases
        value = re.sub(r"(?<![ ])\"'", "&rdquo;&rsquo;", value)
        value = re.sub(r"\"'(?![ ])", "&ldquo;&lsquo;", value)
        value = re.sub(r"(?<![ ])'\"", "&rsquo;&rdquo;", value)
        value = re.sub(r"'\"(?![ ])", "&lsquo;&ldquo;", value)

        # Single quotes (turn right first for apostrophes
        value = re.sub(r"(?<![ ])'", "&rsquo;", value)
        value = re.sub(r"'(?![ ])", "&lsquo;", value)

        # Double quotes
        value = re.sub(r"(?<![ ])\"", "&rdquo;", value)
        value = re.sub(r"\"(?![ ])", "&ldquo;", value)

        # Remove minor hack
        value = value[1:-1]

        value = value.replace('/n', '\n')
        out += value
    return out


def get_lexer(language):
    # Checks custom lexers first
    custom_lexers = {
        'obj-c': RysObjectiveCLexer(),
        'git': RysGitLexer(),
        'git-out': RysGitOutputLexer(),
    }

    if language in custom_lexers:
        return custom_lexers[language]
    else:
        return get_lexer_by_name(language)
