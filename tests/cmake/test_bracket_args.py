from ros_build_assistant.parser.cmake.grammar import BracketArgument

def parse_item(inp):
    ba = BracketArgument()
    for x in inp:
        res, data = ba.next_char(x)
    return res,data

print(parse_item("[[Hello world]]"))
print(parse_item("[[Hello world]=]"))
print(parse_item("[=[Hello world]=]"))
print(parse_item("[==[Hello world]=]==]"))