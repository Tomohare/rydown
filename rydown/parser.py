import re
import ply.yacc as yacc
from lexer import MarkdownLexer


class MarkdownParser:

    precedence = (
        ('left', 'PLAINTEXT'),
        ('left', 'EMPHASISSTRONG', 'EMPHASIS',
            'STRONG', 'INLINE_CODE', 'LINK_URL'),
        ('left', 'BLOCK_CODE'),
    )

    def __init__(self):
        self.max_heading_level = 0
        self.ref_link_table = {}
        self.list_stack = []
        self.lexer = MarkdownLexer()
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self, write_tables=1)

    def parse(self, text):
        self.max_heading_level = 0
        self.ref_link_table = {}
        self.list_stack = []
        # Reset the lexer state (this is very important!)
        self.lexer.reset()
        # Replace for good indentation (HACK :\)
        text = text.replace('  ', '\x80\x80')
        text = text.replace('\t', '\x81\x81')
        tree = self.parser.parse(text.lstrip(), debug=False)
        self.r_node(tree)
        return tree

    def p_document(self, p):
        '''document :
                    | document block'''
        if len(p) == 1:
            p[0] = ['document', []]
        else:
            p[0] = ['document', p[1][1] + [p[2]]]

    def p_block(self, p):
        '''block : heading
                 | subheading
                 | paragraph
                 | figure
                 | ulist
                 | olist
                 | block_code
                 | blockercode
                 | blockquote
                 | horizontalline
                 | table
                 | ref_link_url'''
        p[0] = p[1]

    def p_olist(self, p):
        '''olist : olist_item
                | olist olist_item'''
        if len(p) == 2:
            p[0] = ['olist', [p[1]]]
        else:
            p[0] = ['olist', p[1][1] + [p[2]]]

    def p_olist_item(self, p):
        '''olist_item : OLIST_ITEM_START phrase_list
                      | OLIST_ITEM_START phrase_list LIST_END
                      | OLIST_ITEM_START phrase_list SINGLE_NEWLINE olist_2
                      | OLIST_ITEM_START phrase_list SINGLE_NEWLINE ulist'''
        if len(p) == 3 or len(p) == 4:
            # Contains a phrase list or is the last item
            p[0] = ['list_item', p[2]]
        elif len(p) == 5:
            # Contains a nested list after the phrase list
            # Need this to make the nested list part of the previous list_item
            p[0] = ['list_item', p[2] + [p[4]]]

    def p_olist_2(self, p):
        '''olist_2 : olist_item_2
                   | olist_2 olist_item_2'''
        if len(p) == 2:
            p[0] = ['olist', [p[1]]]
        else:
            p[0] = ['olist', p[1][1] + [p[2]]]

    def p_olist_item_2(self, p):
        '''olist_item_2 : OLIST_ITEM_2_START phrase_list
                       | OLIST_ITEM_2_START phrase_list LIST_END
                       | OLIST_ITEM_2_START phrase_list SINGLE_NEWLINE olist_3
                       | OLIST_ITEM_2_START phrase_list SINGLE_NEWLINE ulist'''
        if len(p) == 3 or len(p) == 4:
            # Contains a phrase list or is the last item
            p[0] = ['list_item', p[2]]
        elif len(p) == 5:
            # Contains a nested list after the phrase list
            # Need this to make the nested list part of the previous list_item
            p[0] = ['list_item', p[2] + [p[4]]]

    def p_olist_3(self, p):
        '''olist_3 : olist_item_3
                   | olist_3 olist_item_3'''
        if len(p) == 2:
            p[0] = ['olist', [p[1]]]
        else:
            p[0] = ['olist', p[1][1] + [p[2]]]

    def p_olist_item_3(self, p):
        '''olist_item_3 : OLIST_ITEM_3_START phrase_list
                       | OLIST_ITEM_3_START phrase_list LIST_END
                       | OLIST_ITEM_3_START phrase_list SINGLE_NEWLINE olist_4
                       | OLIST_ITEM_3_START phrase_list SINGLE_NEWLINE ulist'''
        if len(p) == 3 or len(p) == 4:
            # Contains a phrase list or is the last item
            p[0] = ['list_item', p[2]]
        elif len(p) == 5:
            # Contains a nested list after the phrase list
            # Need this to make the nested list part of the previous list_item
            p[0] = ['list_item', p[2] + [p[4]]]

    def p_olist_4(self, p):
        '''olist_4 : olist_item_4
                  | olist_4 olist_item_4'''
        if len(p) == 2:
            p[0] = ['olist', [p[1]]]
        else:
            p[0] = ['olist', p[1][1] + [p[2]]]

    def p_olist_item_4(self, p):
        '''olist_item_4 : OLIST_ITEM_4_START phrase_list
                        | OLIST_ITEM_4_START phrase_list LIST_END'''
        # There is a maximum of 4 nested lists
        p[0] = ['list_item', p[2]]

    def p_ulist(self, p):
        '''ulist : ulist_item
                | ulist ulist_item'''
        if len(p) == 2:
            p[0] = ['ulist', [p[1]]]
        else:
            p[0] = ['ulist', p[1][1] + [p[2]]]

    def p_ulist_item(self, p):
        '''ulist_item : ULIST_ITEM_START phrase_list
                      | ULIST_ITEM_START phrase_list LIST_END
                      | ULIST_ITEM_START phrase_list SINGLE_NEWLINE olist_2'''
        numsps = re.search('(\x80\x80)*', p[1]).end()
        numtab = re.search('(\x81\x81)*', p[1]).end()
        if numsps > 0:
            p[1] = str(int(numsps / 2))
        elif numtab > 0:
            p[1] = str(int(numtab / 2))
        else:
            p[1] = '0'
        if len(p) >= 3 and len(p) <= 4:
            # Contains a phrase list or is the last item and the identation
            p[0] = ['list_uitem', p[2] + [p[1]]]
        elif len(p) == 5:
            # Contains a nested list after the phrase list
            # Need this to make the nested list part of the previous list_item
            p[0] = ['list_uitem', p[2] + [p[4]]]

    def p_heading(self, p):
        '''heading : HEADING_START phrase_list HEADING_END SINGLE_NEWLINE
                   | HEADING_START phrase bothendlines'''
        level = len(p[1].strip())
        if level > self.max_heading_level:
            self.max_heading_level = level
        p[0] = ['heading', [p[2]], level]

    def p_subheading(self, p):
        '''subheading : phrase_list SINGLE_NEWLINE UNDERDIVIDER bothendlines
                    | phrase_list SINGLE_NEWLINE HORIZONTALLINE bothendlines'''
        p[0] = ['subheading', p[1]]

    def p_horizontalline(self, p):
        '''horizontalline : MULTIPLE_NEWLINES HORIZONTALLINE MULTIPLE_NEWLINES'''  # noqa
        p[0] = ['horizontalline']

    def p_paragraph(self, p):
        '''paragraph : phrase_list MULTIPLE_NEWLINES'''
        p[0] = ['paragraph', p[1]]

    def p_figure(self, p):
        '''figure : FIG_START phrase_list FIG_URL MULTIPLE_NEWLINES'''
        p[0] = ['figure', p[2], p[3]]

    def p_table_body(self, p):
        '''table_body : TCONTENT SINGLE_NEWLINE table_body
                      | TCONTENT SINGLE_NEWLINE
                      | TCONTENT'''
        if len(p) == 4:
            p[0] = ['table_body', p[1], p[3]]
        else:
            p[0] = ['table_body', p[1]]

    def p_table(self, p):
        '''table : TCONTENT SINGLE_NEWLINE TMARKER SINGLE_NEWLINE table_body bothendlines'''  # noqa
        p[0] = ['table_head', p[1], p[5]]

    def p_block_code(self, p):
        '''block_code : BLOCK_CODE'''
        # Indent was removed in lexer
        # Check for a language identifier
        code = p[1]
        language = ''
        if code[:3] == ":::":
            # Extract the identifier
            language = re.match(r'^:::(.*)\n', code).group(1)
            # Remove the line
            code = re.sub(r'^.*\n', '', code)
        p[0] = ['block_code', code, language]

    def p_blockercode(self, p):
        '''blockercode : BLOCKERCODEONE bothendlines
                       | BLOCKERCODETWO bothendlines'''
        p[1] = p[1].replace('\x80\x80', '  ')
        p[1] = p[1].replace('\x81\x81', '\t')
        language = p[1][3:].split('\n')[0]
        code = '\n'.join(p[1][3:-3].split('\n')[1:])
        p[0] = ['blocker_code', code, language]

    def p_blockquote(self, p):
        '''blockquote : BLOCKQUOTE phrase_list MULTIPLE_NEWLINES
                      | BLOCKQUOTE phrase_list blockquote
                      | BLOCKQUOTE SINGLE_NEWLINE blockquote
                      | BLOCKQUOTE MULTIPLE_NEWLINES'''
        if len(p) == 2:
            p[0] = [p[1]]
        elif p[2] == '\n':
            p[0] = ['blockquote', [['text', ' '], ['text', '\n']] + p[3][1]]
        elif len(p) > 2 and p[3] != '\n\n':
            if isinstance(p[3][1], list):
                p[0] = ['blockquote', p[2] + p[3][1]]
            else:
                p[0] = ['blockquote', p[2]]
        else:
            p[0] = ['blockquote', p[2]]

    def p_phrase_list(self, p):
        '''phrase_list : phrase
                       | phrase_list phrase'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_phrase(self, p):
        '''phrase : link
                  | ref_link
                  | emphasisstrong
                  | emphasis
                  | strong
                  | inline_code
                  | COMMENT
                  | text'''
        p[0] = p[1]

    def p_emphasisstrong(self, p):
        '''emphasisstrong : EMPHASISSTRONG'''
        p[0] = ['emphasisstrong', p[1]]

    def p_emphasis(self, p):
        '''emphasis : EMPHASIS'''
        p[0] = ['emphasis', p[1]]

    def p_strong(self, p):
        '''strong : STRONG'''
        p[0] = ['strong', p[1]]

    def p_inline_code(self, p):
        '''inline_code : INLINE_CODE'''
        # INLINE_CODE token switches lexer state
        p[0] = ['inline_code', p[1]]

    def p_link(self, p):
        '''link : LINK_START phrase_list LINK_URL'''
        p[0] = ['link', p[2], p[3]]

    def p_ref_link(self, p):
        '''ref_link : REF_LINK_START phrase_list REF_LINK_KEY'''
        p[0] = ['ref_link', p[2], p[3]]

    def p_ref_link_url(self, p):
        '''ref_link_url : REF_LINK_URL bothendlines'''
        # Store reference links in a table
        vals = p[1].split(':', 1)
        key = vals[0].strip()[1:-1]
        url = vals[1].strip()
        # Don't actually need this below
        p[0] = ['ref_link_url', key, url]

        self.ref_link_table[key] = url

    def p_text(self, p):
        '''text : PLAINTEXT
                | TCONTENT
                | LINK_SPECIAL_CHARS
                | SINGLE_NEWLINE
                | ESCAPE_SEQUENCE'''
        p[1] = p[1].replace('\x80\x80', '  ')
        p[1] = p[1].replace('\x81\x81', '\t')
        p[0] = ['text', p[1]]

    def p_bothendlines(self, p):
        ''' bothendlines : SINGLE_NEWLINE
                         | MULTIPLE_NEWLINES'''
        p[0] = p[1]

    def p_error(self, p):
        print("Syntax error on token: %s" % p)

    def r_node(self, node, parent=None):
        # Really need to abstract this tree traversal
        node_type = node[0]
        if node_type == 'document':
            for block in node[1]:
                self.r_node(block, node)

        elif node_type == 'heading':
            # Invert heading levels (not doing this right now)
            # node[2] = self.max_heading_level - node[2] + 1
            for phrase in node[1]:
                self.r_node(phrase, node)

        elif node_type == 'table':
            for element in node[1]:
                self.r_node(element, node)

        elif node_type == 'table_head':
            for element in node[1]:
                self.r_node(element, node)

        elif node_type == 'table_body':
            for element in node[1]:
                self.r_node(element, node)

        elif node_type == 'subheading':
            self.r_node(node[1], node)

        elif node_type == 'paragraph':
            for phrase in node[1]:
                self.r_node(phrase, node)

        elif node_type == 'emphasisstrong':
            for phrase in node[1]:
                self.r_node(phrase, node)

        elif node_type == 'emphasis':
            for phrase in node[1]:
                self.r_node(phrase, node)

        elif node_type == 'strong':
            for phrase in node[1]:
                self.r_node(phrase, node)

        elif node_type == 'inline_code':
            self.r_node(node[1], node)

        elif node_type == 'ref_link':
            # Add the URL as another field (want to preserve they key)
            key = node[2]
            url = self.ref_link_table[key]
            node.append(url)
            self.r_node(node[1], node)

        elif node_type == 'list':
            for phrase in node[1]:
                self.r_node(phrase, node)

        elif node_type == 'list_item':
            for phrase in node[1]:
                self.r_node(phrase, node)

        elif node_type == 'list_uitem':
            for phrase in node[1]:
                self.r_node(phrase, node)
