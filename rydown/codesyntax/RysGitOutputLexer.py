from pygments.lexer import RegexLexer, bygroups
from pygments.token import (Comment, Keyword, Text, Name, String)


# Need pick squash, etc.
# And reflog


class RysGitOutputLexer(RegexLexer):
    tokens = {
        'root': [
            (r'(commit)(\s)(\w{40})$',
             bygroups(Keyword, Text, String), 'default-log'),
            (r'#', Comment, 'comment'),
            (r'(\*?[a-zA-Z0-9]{7})( HEAD@{\d}: )(.+)',
             bygroups(String, Name.Label, Text)),  # Reflog
            (r'(\*?[a-zA-Z0-9]{7})(.+)',
             bygroups(String, Text)),       # Short log
            # Interactive rebase
            (r'(pick|squash|edit)( )([a-zA-Z0-9]{7})(.+)',
             bygroups(Keyword, Text, String, Text)),
            (r'...', Text),  # Ellipsis
        ],
        'default-log': [
            (r'[ ]+|\n', Text),
            (r'(\w+:)(\s+)(.+)', bygroups(Name.Label, Text, String)),
            (r'.+', Text)
        ],
        'short-log': [
            # FINISH HERE
        ],
        'comment': [
            (r'[ ]+|\n', Text),
            (r'(On branch )(\S+)',                              # Branch output
             bygroups(Comment, Comment.Special)),
            (r'Not currently on any branch.', Comment),
            (r'(#\s{4,})(.*)',                                  # File list
             bygroups(Comment, Comment.Special)),
            (r'(# )?(.*:)', bygroups(Comment, Comment.Special)),  # Label
            (r'(#.*)', Comment),                                # Generic
            # Anything else
            (r'^.+', Text),
        ],
    }
