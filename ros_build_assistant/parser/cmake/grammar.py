import enum

class CombinatorState(enum.Enum):
    FINISHED = 0 #We finished parsing the item
    FINISHED_ONE_AFTER = 2 #For cases where look ahead is needed
    IN_PROGRESS = 1 #When the parser is parsing
    ERROR = -1 #When the parser fails


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
        if self.num_equals == 0:
            return "[["
        return "["+ ("="*self.num_equals) + "["
        
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
        if self.num_equals == 0:
            return "]]"
        return "]"+ ("="*self.num_equals) + "]"


class BracketArgument:
    
    def __init__(self):
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


