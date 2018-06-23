import re

from pygments.lexer import RegexLexer, include, bygroups, using, \
    this
from pygments.token import Text, Comment, Operator, Keyword, Name, String, \
    Number, Punctuation, Literal


class RysObjectiveCLexer(RegexLexer):
    """Custom Objective-C source code with additional compiler directives

    - Added @-directives:
        - @autorelease
        - @required
        - @optional

    - Changed keyword values from Name.Built to Keyword.
      Constant and added a few:
        - YES
        - NO
        - Nil

    - Added variable modifiers as Keyword.Type:
        - __block
        - __weak
        - __strong

    - Moved plain Keywords to Keyword.Type:
        - const
        - static

    - "Fixed" method call highlighting:
        - Changed from Name.Label to Name.Function
        - Added support for parameterless method calls (a bit hackish)

    - Added NS.* as Name.Builtin

    - Add import and define as special preprocessor directives

    - Add dedicated pattern for class extensions

    - Add protocol support
        - First method in formal protocol wasn't being highlighted
        - Add @protocol() directive as keyword
        - I don't think protocols were supported beyond forward-declarations

    - Add array and dictionary literals (no numbers though)

    - Fix function declaration highlighting
        - This broke something: functions implemented after main() are not
          highlighted properly.

    - Add fixed width integer types from inttype.h

    - Add integer literals

    - Add Boolean literals

    - Add @() literal boxing syntax

    - Add arc4random_uniform() and arc4random() as Name.Builtin

    - Fix top-level NSLog() highlighting
        - Was highlighting last letter of function calls in standalone snippets

    - Add @property attribute keywords
    """

    name = 'Objective-C'
    aliases = ['objective-c', 'objectivec', 'obj-c', 'objc']
    # XXX: objc has .h files too :-/   ... and .mm. Who wrote this?
    filenames = ['*.m']
    mimetypes = ['text/x-objective-c']

    #: optional Comment or Whitespace
    _ws = r'(?:\s|//.*?\n|/[*].*?[*]/)+'

    tokens = {
        'whitespace': [
            # preprocessor directives: without whitespace
            ('^#if\s+0', Comment.Preproc, 'if0'),
            ('^#', Comment.Preproc, 'macro'),
            # or with whitespace
            ('^' + _ws + r'#if\s+0', Comment.Preproc, 'if0'),
            # Next line doesn't allow comments before import statements...
            # ('^' + _ws + '#', Comment.Preproc, 'macro'),
            (r'\n', Text),
            (r'\s+', Text),
            (r'\\\n', Text),  # line continuation
            (r'//(\n|(.|\n)*?[^\\]\n)', Comment.Single),
            (r'/(\\\n)?[*](.|\n)*?[*](\\\n)?/', Comment.Multiline),
        ],
        'statements': [
            # Parameterless methods (a bit hackish)
            (r'(\[)([a-zA-Z$_][a-zA-Z0-9$_]*)(\s+)'
             r'([a-zA-Z$_][a-zA-Z0-9$_]*)(\])',
                bygroups(Punctuation, Name, Text, Name.Function, Punctuation)),
            # alloc/init (really hackish)
            (r'(init)(\])', bygroups(Name.Function, Punctuation)),
            (r'(L|@)?"', String, 'string'),
            (r"(L|@)?'(\\.|\\[0-7]{1,3}|\\x[a-fA-F0-9]{1,2}|[^\\\'\n])'",
             String.Char),
            (r'(L|@)?\[', Punctuation),  # Literal array
            (r'(L|@)?\{', Punctuation),  # Literal dictionary
            (r'@\(', Punctuation),  # Literal boxed expression
            (r'@\d+', Number),  # Literal integer
            (r'@YES|@NO', Keyword.Constant),  # Literal Boolean
            (r'(\d+\.\d*|\.\d+|\d+)[eE][+-]?\d+[lL]?', Number.Float),
            (r'(\d+\.\d*|\.\d+|\d+[fF])[fF]?', Number.Float),
            (r'0x[0-9a-fA-F]+[Ll]?', Number.Hex),
            # Protocol as a data type
            (r'<[a-zA-Z$_][a-zA-Z0-9$_]*>', Name.Label),
            (r'0[0-7]+[Ll]?', Number.Oct),
            (r'\d+[Ll]?', Number.Integer),
            (r'[~!%^&*+=|?:<>/-]', Operator),
            (r'[()\[\],.]', Punctuation),
            (r'(auto|break|case|continue|default|do|else|enum|extern|'
             r'for|goto|if|register|restricted|return|sizeof|struct|'
             r'switch|typedef|union|volatile|virtual|while|in|@selector|'
             r'@private|@protected|@public|@encode|'
             r'@synchronized|@try|@throw|@catch|@finally|@end|@property|'
             r'@synthesize|@dynamic|@autoreleasepool|@required|@optional|'
             r'@protocol|@blc|copy|nonatomic|readonly|readwrite|strong|'
             r'weak|getter|setter)\b', Keyword),
            # Custom typedefs used in my tutorials (shouldn't really be
            # here...)
            (r'SpeedFunction', Keyword.Type),
            (r'(int|long|float|short|double|char|unsigned|signed|'
             r'void|id|BOOL|IBOutlet|IBAction|SEL|Class|__block|'
             r'__weak|unichar|int8_t|uint8_t|int16_t|uint16_t|'
             r'int32_t|uint32_t|int64_t|uint64_t|int_least8_t|'
             r'uint_least8_t|int_least16_t|uint_least16_t|'
             r'int_least32_t|uint_least32_t|int_least64_t|'
             r'uint_least64_t|intmax_t|uintmax_t|intptr_t|uintptr_t|'
             r'size_t|__strong|const|static)\b', Keyword.Type),
            (r'(_{0,2}inline|naked|restrict|thread|typename)\b',
                Keyword.Reserved),
            (r'__(asm|int8|based|except|int16|stdcall|cdecl|fastcall|int32|'
             r'declspec|finally|int64|try|leave)\b', Keyword.Reserved),
            (r'(TRUE|FALSE|nil|NULL|Nil|YES|NO|self)\b', Keyword.Constant),
            # Custom built-in functions
            (r'(arc4random_uniform|arc4random)\b', Name.Builtin),
            # Highlight method calls that take parameters
            ('[a-zA-Z$_][a-zA-Z0-9$_]*:(?!:)', Name.Function),
            # NSArray, NSString, etc.
            (r'NS[a-zA-Z0-9$_]*', Name.Builtin),
            # Everything else
            ('[a-zA-Z$_][a-zA-Z0-9$_]*', Name),
        ],
        'root': [
            include('whitespace'),
            # functions
            (r'((?:[a-zA-Z0-9_*\s])+?(?:\s|[*]))'    # return arguments
             r'([a-zA-Z$_][a-zA-Z0-9$_]*)'           # method name
             r'(\s*\([^;]*?\))'                      # signature
             r'(' + _ws + r')({)',
             bygroups(using(this), Name.Function,
                      using(this), Text, Punctuation),
             'function'),
            # methods
            (r'^([-+])(\s*)'                         # method marker
             r'(\(.*?\))?(\s*)'                      # return type
             r'([a-zA-Z$_][a-zA-Z0-9$_]*:?)',        # begin of method name
             bygroups(Keyword, Text, using(this),
                      Text, Name.Function),
             'method'),

            # built-in function call (hackish)
            (r'(NS[a-zA-Z0-9$_]*)'                    # NSLog
             r'(\s*\(.*\)\s*)(;)',                    # (...);
             bygroups(Name.Builtin, using(this), Operator)),


            # function call (not really used?)
            (r'([a-zA-Z$_][a-zA-Z0-9$_]*)'            # getRandomInteger
             r'(\s*\(.*\)\s*)(;)',                    # (...);
             bygroups(Name, using(this), Operator)),


            # custom function declarations (hackish)
            (r'([a-zA-Z$_][a-zA-Z0-9$_]*)(\s*)(\*?)'  # int
             r'([a-zA-Z$_][a-zA-Z0-9$_]*)'            # getRandomInteger
             r'(\s*\(.*\)\s*)(;)',                    # (...);
             bygroups(using(this),
                      Text, Operator, Name.Function, using(this), Operator)),




            (r'([a-zA-Z$_][a-zA-Z0-9$_]*)(\s*)'       # static
             r'([a-zA-Z$_][a-zA-Z0-9$_]*)(\s*)(\*?)'  # int
             r'([a-zA-Z$_][a-zA-Z0-9$_]*)'            # getRandomInteger
             r'(\s*\(.*\)\s*)(;)',                    # (...);
             bygroups(using(this), Text, using(this),
                      Text, Operator, Name.Function, using(this), Operator)),

            # function declarations
            (r'((?:[a-zA-Z0-9_*\s])+?(?:\s|[*]))'    # return arguments
             r'([a-zA-Z$_][a-zA-Z0-9$_]*)'           # method name
             r'(\s*\([^;]*?\))'                      # signature
             r'(' + _ws + r')(;)',
             bygroups(using(this), Name.Function,
                      using(this), Text, Punctuation)),
            (r'(@interface|@implementation|@protocol)(\s+)',
             bygroups(Keyword, Text),
             'classname'),
            (r'(@class)(\s+)', bygroups(Keyword, Text),
             'forward_classname'),
            (r'(\s*)(@end)(\s*)', bygroups(Text, Keyword, Text)),
            ('', Text, 'statement'),
        ],
        'classname': [
            # adopting formal protocols (only for inherited classes?)
            ('([a-zA-Z$_][a-zA-Z0-9$_]*)(\s*:\s*)([a-zA-Z$_][a-zA-Z0-9$_]*)'
             '(\s*)(<[a-zA-Z$_][a-zA-Z0-9$_]*>)',
             bygroups(Name.Class, Text, Name.Class, Text, Name.Label), '#pop'),
            # interface definition that inherits
            ('([a-zA-Z$_][a-zA-Z0-9$_]*)(\s*:\s*)([a-zA-Z$_][a-zA-Z0-9$_]*)?',
             bygroups(Name.Class, Text, Name.Class), '#pop'),
            # interface definition for a category
            ('([a-zA-Z$_][a-zA-Z0-9$_]*)(\s*)(\([a-zA-Z$_][a-zA-Z0-9$_]*\))',
             bygroups(Name.Class, Text, Name.Label), '#pop'),
            # interface definition for an extension
            ('([a-zA-Z$_][a-zA-Z0-9$_]*)(\s*)(\(\))',
             bygroups(Name.Class, Text, Name.Label), '#pop'),
            # formal protocol declaration
            ('([a-zA-Z$_][a-zA-Z0-9$_]*)(\s*)(<[a-zA-Z$_][a-zA-Z0-9$_]*>)',
             bygroups(Name.Class, Text, Name.Label), '#pop'),
            # simple interface / implementation
            ('([a-zA-Z$_][a-zA-Z0-9$_]*)', Name.Class, '#pop'),
        ],
        'forward_classname': [
            ('([a-zA-Z$_][a-zA-Z0-9$_]*)(\s*,\s*)',
             bygroups(Name.Class, Text), 'forward_classname'),
            ('([a-zA-Z$_][a-zA-Z0-9$_]*)(\s*;?)',
                bygroups(Name.Class, Text), '#pop')
        ],
        'statement': [
            include('whitespace'),
            include('statements'),
            ('[{}]', Punctuation),
            (';', Punctuation, '#pop'),
        ],
        'function': [
            include('whitespace'),
            include('statements'),
            (';', Punctuation),
            ('{', Punctuation, '#push'),
            ('}', Punctuation, '#pop'),
        ],
        'method': [
            include('whitespace'),
            (r'(\(.*?\))([a-zA-Z$_][a-zA-Z0-9$_]*)', bygroups(using(this),
                                                              Name.Variable)),
            (r'[a-zA-Z$_][a-zA-Z0-9$_]*:', Name.Function),
            (';', Punctuation, '#pop'),
            ('{', Punctuation, 'function'),
            ('', Text, '#pop'),
        ],
        'string': [
            (r'"', String, '#pop'),
            (r'\\([\\abfnrtv"\']|x[a-fA-F0-9]{2,4}|[0-7]{1,3})',
             String.Escape),
            (r'[^\\"\n]+', String),  # all other characters
            (r'\\\n', String),  # line continuation
            (r'\\', String),  # stray backslash
        ],
        'macro': [
            (r'(import|define)(\s+)(.*)',
             bygroups(Comment.Preproc, Text, Literal)),
            (r'[^/\n]+', Comment.Preproc),
            (r'/[*](.|\n)*?[*]/', Comment.Multiline),
            (r'//.*?\n', Comment.Single, '#pop'),
            (r'/', Comment.Preproc),
            (r'(?<=\\)\n', Comment.Preproc),
            (r'\n', Comment.Preproc, '#pop'),
        ],
        'if0': [
            (r'^\s*#if.*?(?<!\\)\n', Comment.Preproc, '#push'),
            (r'^\s*#endif.*?(?<!\\)\n', Comment.Preproc, '#pop'),
            (r'.*?\n', Comment),
        ]
    }

    def analyse_text(text):
        if '@import' in text or '@interface' in text or \
                '@implementation' in text:
            return True
        elif '@"' in text:  # strings
            return True
        elif re.match(r'\[[a-zA-Z0-9.]:', text):  # message
            return True
        return False
