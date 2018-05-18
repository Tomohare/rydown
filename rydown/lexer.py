# -*- encoding: utf-8; -*-
import re
import textwrap
import ply.lex as lex


class MarkdownLexer:

    def __init__(self):
        self.lexer = lex.lex(module=self, debug=False)

    def reset(self):
        # Call this before running the lexer a second time
        self.state = 'INITIAL'
        self.lexer.begin('INITIAL')

    state = 'INITIAL'

    states = (
        ('link', 'inclusive'),
        ('reflink', 'inclusive'),
        ('figure', 'inclusive'),
        ('list', 'inclusive'),
        ('heading', 'inclusive'),
        ('table', 'inclusive'),
    )

    # Tokens
    tokens = [
        "HEADING_START",
        "HEADING_END",
        "UNDERDIVIDER",
        "HORIZONTALLINE",
        "BLOCKQUOTE",
        "EMPHASISSTRONG",
        "STRONG",
        "EMPHASIS",
        "INLINE_CODE",
        "BLOCK_CODE",
        "BLOCKERCODEONE",
        "BLOCKERCODETWO",
        "PLAINTEXT",
        "LINK_START",
        "LINK_URL",
        "LINK_SPECIAL_CHARS",
        "REF_LINK_START",
        "REF_LINK_KEY",
        "REF_LINK_URL",
        "TMARKER",
        "TCONTENT",
        "OLIST_ITEM_START",
        "OLIST_ITEM_2_START",
        "OLIST_ITEM_3_START",
        "OLIST_ITEM_4_START",
        "ULIST_ITEM_START",
        "LIST_END",
        "FIG_START",
        "FIG_URL",
        "MULTIPLE_NEWLINES",
        "SINGLE_NEWLINE",
        "COMMENT",
        "ESCAPE_SEQUENCE",
    ]

    t_PLAINTEXT = r'[^`*\n\t\\\[\]]+'
    t_LINK_SPECIAL_CHARS = r'[\[\]]'
    t_REF_LINK_URL = r'\[[^\]\s]+\]\s*:\s*.+'

    def t_HEADING_START(self, t):
        r'\#{1,6}\ '
        t.lexer.push_state('heading')
        return t

    def t_HEADING_END(self, t):
        r'\ \#{1,6}'
        t.lexer.pop_state()
        return t

    def t_heading_PLAINTEXT(self, t):
        r'[^`*\n\t#\\\[\]]+(?=[^#])'
        # Need to disallow # in headings
        # Dunno why the [^#] works (for heading strip)
        return t

    def t_HORIZONTALLINE(self, t):
        r'-{3,}'
        t.value = '----'
        return t

    def t_EMPHASISSTRONG(self, t):
        r'\*\*\*([^ ][^*]+[^ ]|[^* ]+)\*\*\*'
        t.value = t.value[3:-3]
        return t

    def t_STRONG(self, t):
        r'\*\*([^ ][^*]+[^ ]|[^* ]+)\*\*'
        t.value = t.value[2:-2]
        return t

    def t_EMPHASIS(self, t):
        r'\*([^ ][^*]+[^ ]|[^* ]+)\*'
        t.value = t.value[1:-1]
        return t

    def t_UNDERDIVIDER(self, t):
        r'[=-]{2,}'
        return t

    def t_BLOCKQUOTE(self, t):
        r'>|>\s'
        return t

    def t_table_TMARKER(self, t):
        r'([\|]?(:-:|:-|-:|-)[\|]?)+'
        return t

    def t_TCONTENT(self, t):
        r'([-\wb ]+\|[-\wb ]+\|([-\wb ]*\|*)+)+'
        if self.state != 'table':
            self.state = 'table'
            t.lexer.push_state('table')
        return t

    def t_OLIST_ITEM_START(self, t):
        r'\d+\.\s'
        # Change state to `list` if this is first item
        if self.state != 'list':
            self.state = 'list'
            t.lexer.push_state('list')
        return t

    def t_list_OLIST_ITEM_2_START(self, t):
        r'\t\d+\.\s'
        return t

    def t_list_OLIST_ITEM_3_START(self, t):
        r'\t\t\d+\.\s'
        return t

    def t_list_OLIST_ITEM_4_START(self, t):
        r'\t\t\t\d+\.\s'
        return t

    def t_ULIST_ITEM_START(self, t):
        r'((\x81\x81|\x80\x80)*)([*+-][\t ]+)'
        # Change state to `list` if this is first item
        if self.state != 'list':
            self.state = 'list'
            t.lexer.push_state('list')
        return t

    def t_list_LIST_END(self, t):
        r'\n\n+(?!\n)'
        # Reset state
        if t.lexer.current_state() == 'list':
            self.state = 'INITIAL'
            t.lexer.pop_state()
        return t

    def t_BLOCK_CODE(self, t):
        r'\t(.*\n\t)*(.+\n\n+)'
        # [start]     [line]+        [end]
        # If you want to allow empty lines: r'\t   (.+\n+\t)+   (.+\n\n(?!\t))'
        # Dedent the code block
        t.value = textwrap.dedent(t.value)
        return t

    def t_BLOCKERCODEONE(self, t):
        r'[`~]{3}[^\n\`]((?!```).|(?!```)\n|)*[`~]{3}'
        t.value = textwrap.dedent(t.value)
        return t

    def t_BLOCKERCODETWO(self, t):
        r'[`~]{3}((?!```).|(?!```)\n|)*[`~]{3}'
        t.value = textwrap.dedent('```text' + t.value[3:])
        return t

    # Fig regexs were (basically) copied from link tokens
    def t_FIG_START(self, t):
        r'!\[(?=([^\]\[]|\n)+\]\([^\s]+\))'
        # Must make sure this isn't too greedy
        t.lexer.push_state('figure')
        return t

    def t_figure_FIG_URL(self, t):
        r'\]\([^\s]+\)'
        t.value = t.value[2:-1]
        t.lexer.pop_state()
        return t

    def t_LINK_START(self, t):
        r'\[(?=([^\]\[]|\n)+\]\([^\s]+\))'
        # Must make sure this isn't too greedy
        t.lexer.push_state('link')
        return t

    def t_link_LINK_URL(self, t):
        r'\]\([^\s]+\)'
        t.value = t.value[2:-1]
        t.lexer.pop_state()
        return t

    def t_REF_LINK_START(self, t):
        r'\[(?=([^\]\[]|\n)+\]\[[^\s]+\])'
        t.lexer.push_state('reflink')
        return t

    def t_reflink_REF_LINK_KEY(self, t):
        r'\]\[[^\s]+\]'
        t.value = t.value[2:-1]
        t.lexer.pop_state()
        return t

    def t_INLINE_CODE(self, t):
        r'\`[^\`]+\`'
        # Processes plaintext verbatim until the closing token
        # Replace newlines with spaces
        t.value = re.sub(r'\n+', ' ', t.value)
        # Remove the surrounding backticks
        t.value = t.value[1:-1]
        return t

    def t_ESCAPE_SEQUENCE(self, t):
        r"(\\\\)|(\\[^\\\s]{1})"
        t.value = t.value[1]
        return t

    def t_COMMENT(self, t):
        r'<!?--(?:(?!-->)(.|\n|\s))*-->\n*'
        pass

    def t_MULTIPLE_NEWLINES(self, t):
        r'\n{2,}|\n$'
        # Since the header is never poped if we don't
        #  have end special character we do it ourselves
        if t.lexer.current_state() in ['heading', 'table']:
            t.lexer.pop_state()
        elif t.lexer.current_state() == 'list':
            self.state = 'INITIAL'
            t.lexer.pop_state()
        t.lexer.lineno += len(t.value)
        return t

    def t_SINGLE_NEWLINE(self, t):
        r'\n'
        # Since the header is never poped if we don't
        #  have end special character we do it ourselves
        if t.lexer.current_state() == 'heading':
            t.lexer.pop_state()
        t.lexer.lineno += 1
        return t

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)
