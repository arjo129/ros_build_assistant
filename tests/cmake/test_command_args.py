from ros_build_assistant.parser.cmake.grammar import CommandArguments, CombinatorState
import unittest


def parse_item(inp):
    bc = CommandArguments()
    for x in inp:
        res, data = bc.next_char(x)
    return res,data

class TestCommandArguments(unittest.TestCase):
    
    def test_command_arguments(self):
        #normal operation
        inp = "( #[[Hello world]] [[some nonsense (]] (A AND B))"
        res, data = parse_item(inp)
        self.assertEqual(res, CombinatorState.FINISHED)
        out = CommandArguments().code_gen(data)
        self.assertEqual(out, inp)
