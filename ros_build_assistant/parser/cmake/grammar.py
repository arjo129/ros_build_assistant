import enum

"""
This file contains a parser and code generator for parsing and transforming
cmake files. (Yes it's hand written, :( )

Grammar is based on: https://cmake.org/cmake/help/latest/manual/cmake-language.7.html#grammar-token-escape-sequence
"""

class CombinatorState(enum.Enum):
    FINISHED = 0 #We finished parsing the item
    FINISHED_ONE_AFTER = 2 #For cases where look ahead is needed
    IN_PROGRESS = 1 #When the parser is parsing
    ERROR = -1 #When the parser fails

"""
This section defines the rules for a bracketed argument
"""

class BracketOpen:
    def __init__(self):
        self.state = "EXPECT_BRACE"
        self.num_equals = 0

    def reset(self):
        self.state = "EXPECT_BRACE"
        self.num_equals = 0

    def next_char(self, next_char):
        if self.state == "EXPECT_BRACE":
            if "[" == next_char:
                self.state = "WAITING"
                return CombinatorState.IN_PROGRESS, None
            else:
                return CombinatorState.ERROR, None
        elif self.state == "WAITING":
            if "[" == next_char:
                self.state = "DONE"
                return CombinatorState.FINISHED, {"type": "bracket_open", "num_equals": self.num_equals}
            if "=" == next_char:
                self.num_equals += 1
                return CombinatorState.IN_PROGRESS, None
            else:
                return CombinatorState.ERROR, None
            
    def code_gen(self, data):
        if data["num_equals"] == 0:
            return "[["
        return "["+ ("="*data["num_equals"]) + "["


class BracketClose:
    def __init__(self):
        self.state = "EXPECT_BRACE"
        self.num_equals = 0

    def reset(self):
        self.state = "EXPECT_BRACE"
        self.num_equals = 0

    def next_char(self, next_char):
        if self.state == "EXPECT_BRACE":
            if "]" == next_char:
                self.state = "WAITING"
                return CombinatorState.IN_PROGRESS, None
            else:
                return CombinatorState.ERROR, None
        elif self.state == "WAITING":
            if "]" == next_char:
                return CombinatorState.FINISHED, {"type": "bracket_close", "num_equals": self.num_equals}
            if "=" == next_char:
                self.num_equals += 1
                return CombinatorState.IN_PROGRESS, None
            else:
                return CombinatorState.ERROR, None
            
    def code_gen(self, data):
        if data["num_equals"] == 0:
            return "]]"
        return "]"+ ("="*data["num_equals"]) + "]"


class BracketArgument:
    
    def __init__(self):
        self.state = "EXPECT_BRACKET_OPEN"
        self.num_equals = 0
        self.bracket_open = BracketOpen()
        self.bracket_close = BracketClose()
        self.children = []
        self.body = ""
    
    def reset(self):
        self.state = "EXPECT_BRACKET_OPEN"
        self.num_equals = 0
        self.bracket_open = BracketOpen()
        self.bracket_close = BracketClose()
        self.children = []
        self.body = ""

    def next_char(self, next_char):
        if self.state == "EXPECT_BRACKET_OPEN":
            res, data = self.bracket_open.next_char(next_char)
            if res == CombinatorState.FINISHED:
                self.state = "EXPECT_BODY"
                self.num_equals = data["num_equals"]
                self.children.append(data)
                return CombinatorState.IN_PROGRESS, None
            elif res == CombinatorState.ERROR:
                self.bracket_open.reset()
                return CombinatorState.ERROR, None
            else:
                return CombinatorState.IN_PROGRESS, None

        elif self.state == "EXPECT_BODY":
            self.body += next_char
            res, data = self.bracket_close.next_char(next_char)
            if res == CombinatorState.FINISHED:
                if self.num_equals == data["num_equals"]:
                    self.children.append(data)
                    return CombinatorState.FINISHED, {"type": "bracket_args", "num_equals": self.num_equals, "body": self.body[:-2-self.num_equals]}
                else: 
                    self.bracket_close.reset()
                    res, data = self.bracket_close.next_char(next_char)
                    if res == CombinatorState.ERROR:
                        self.bracket_close.reset()
                    return CombinatorState.IN_PROGRESS, None

            elif res == CombinatorState.ERROR:
                self.bracket_close.reset()
                return CombinatorState.IN_PROGRESS, None
            else:
                return CombinatorState.IN_PROGRESS, None

    def code_gen(self, data):
        prefix = self.bracket_open.code_gen({"type": "bracket_open", "num_equals": data["num_equals"]})
        suffix = self.bracket_close.code_gen({"type": "bracket_close", "num_equals": data["num_equals"]})
        return prefix + data["body"] + suffix


"""
This defines the rules for a quoted argument
"""
class QuotedArgument:
    def __init__(self):
        self.state = "EXPECT_QUOTE"
        self.body = ""

    def reset(self):
        self.state = "EXPECT_QUOTE"
        self.body = ""

    def next_char(self, next_char):

        if self.state == "EXPECT_QUOTE":
            if next_char == "\"":
                self.state = "EXPECT_BODY"
                return CombinatorState.IN_PROGRESS, None
            else:
                return CombinatorState.ERROR, None
        
        elif self.state == "EXPECT_BODY":
            if next_char == "\\":
                self.body += next_char
                self.state = "EXPECT_ESCAPE"
                return CombinatorState.IN_PROGRESS, None
            elif next_char == "\"":
                return CombinatorState.FINISHED, {"type": "quoted_argument", "body": self.body}
            else:
                self.body += next_char
                return CombinatorState.IN_PROGRESS, None

        elif self.state == "EXPECT_ESCAPE":
            self.body += next_char
            self.state = "EXPECT_BODY"
            return CombinatorState.IN_PROGRESS, None

    def code_gen(self, data):
        return "\"" + data["body"] + "\""



"""
Handles unquoted_argument including both legacy and modern versions
Note: Finished in this case takes place after a character is read.
"""
class UnQuotedArgument:
    
    def __init__(self):
        self.state = "EXPECT_ITEM"
        self.body = ""
        self.quoted_argument = QuotedArgument()

    def reset(self):
        self.state = "EXPECT_ITEM"
        self.body = ""
        self.quoted_argument = QuotedArgument()

    def next_char(self, next_char):
        
        if self.state == "EXPECT_ITEM":
            if next_char in " ()#\t\r\n;":
                if len(self.body) == 0:
                    return CombinatorState.ERROR, None
                else:
                    return CombinatorState.FINISHED, {"type": "unquoted_argument", "body": self.body}
            elif next_char == "\\":
                self.state = "EXPECT_ESCAPE"
                self.body += next_char
                return CombinatorState.IN_PROGRESS, None
            elif next_char == "\"":
                #stupid legacy behaviour
                self.state = "EXPECT_QUOTE" # can reuse QuotedArgument I guess
                self.quoted_argument.reset()
                self.quoted_argument.next_char(next_char)
                return CombinatorState.IN_PROGRESS, None
            else:
                self.body += next_char
                return CombinatorState.IN_PROGRESS, None
        
        elif self.state == "EXPECT_ESCAPE":
            self.state = "EXPECT_ITEM"
            self.body += next_char
            return CombinatorState.IN_PROGRESS, None
        
        elif self.state == "EXPECT_QUOTE":
            res, data =self.quoted_argument.next_char(next_char)
            if res == CombinatorState.FINISHED:
                self.state = "EXPECT_ITEM"
                self.body += self.quoted_argument.code_gen(data)
            return CombinatorState.IN_PROGRESS, None

    def code_gen(self, data):
        return data["body"]



"""
Handles the line comment.
"""
class LineComment:
    def __init__(self):
        self.state = "EXPECT_HASH"
        self.body = ""

    def reset(self):
        self.state = "EXPECT_HASH"
        self.body = ""

    def next_char(self, next_char):
        if self.state == "EXPECT_HASH":
            if next_char == "#":
                self.state = "EXPECT_BODY"
                return CombinatorState.IN_PROGRESS, None
            else:
                return CombinatorState.ERROR, None

        elif self.state == "EXPECT_BODY":
            if next_char == "\n":
                return CombinatorState.FINISHED, {"type": "line_comment", "body": self.body}
            else:
                self.body += next_char
                return CombinatorState.IN_PROGRESS, None

    def code_gen(self, data):
        return "#" + data["body"] + "\n"


"""
Handles bracket comments
"""
class BracketComment:

    def __init__(self):
        self.state = "EXPECT_HASH"
        self.bracket_argument = BracketArgument()

    def reset(self):
        self.state = "EXPECT_HASH"
        self.bracket_argument = BracketArgument()

    def next_char(self, next_char):
        if self.state == "EXPECT_HASH":
            if next_char == "#":
                self.state = "EXPECT_BRACKET"
                self.bracket_argument.reset()
                return CombinatorState.IN_PROGRESS, None
            else:
                return CombinatorState.ERROR, None
        elif self.state == "EXPECT_BRACKET":
            res, data = self.bracket_argument.next_char(next_char)
            if res == CombinatorState.ERROR:
                return CombinatorState.ERROR, None
            elif res == CombinatorState.FINISHED:
                return CombinatorState.FINISHED, {"type": "bracket_comment", "body": data}
            else:
                return CombinatorState.IN_PROGRESS, None

    def code_gen(self, data):
        return "#"+self.bracket_argument.code_gen(data["body"])

"""
Handles Comments
"""
class Comment:

    def __init__(self):
        self.state = "EXPECT_HASH"
        self.bracket_comment = BracketComment()
        self.line_comment = LineComment()
    
    def next_char(self, next_char):

        if self.state == "EXPECT_HASH":
            self.bracket_comment.reset()
            self.line_comment.reset()
            self.bracket_comment.next_char(next_char)
            res, _ = self.line_comment.next_char(next_char)
            if res == CombinatorState.ERROR:
                return CombinatorState.ERROR, None
            if res == CombinatorState.IN_PROGRESS:
                self.state = "DETERMINE_TYPE"
                return CombinatorState.IN_PROGRESS, None

        elif self.state == "DETERMINE_TYPE":
            res_bc, _  = self.bracket_comment.next_char(next_char)
            res_lc, _ = self.line_comment.next_char(next_char)
            if res_bc == CombinatorState.ERROR:
                if res_lc == CombinatorState.ERROR:
                    return CombinatorState.ERROR, None
                else:
                    self.state = "LINE_COMMENT"
                    return CombinatorState.IN_PROGRESS, None
            else:
                self.state = "BRACKET_COMMENT"
                return CombinatorState.IN_PROGRESS, None
        
        elif self.state == "LINE_COMMENT":
            res, data = self.line_comment.next_char(next_char)
            if res == CombinatorState.FINISHED:
                return CombinatorState.FINISHED, {"type": "comment", "comment": "line", "body": data}
            return res, None

        elif self.state == "BRACKET_COMMENT":
            self.line_comment.next_char(next_char)
            res, data = self.bracket_comment.next_char(next_char)
            if res == CombinatorState.FINISHED:
                return CombinatorState.FINISHED, {"type": "comment", "comment": "bracket", "body": data}

            if res == CombinatorState.ERROR: 
                #Not in grammar spec just here to allow for malformed comments in older files
                #Handles malformatted comments like "#[ Some comment".
                self.state = "LINE_COMMENT"
                return CombinatorState.IN_PROGRESS, None
            return res, None

    def code_gen(self, data):

        if data["comment"] == "line":
            return self.line_comment.code_gen(data["body"])

        elif data["comment"] == "bracket":
            return self.bracket_comment.code_gen(data["body"])