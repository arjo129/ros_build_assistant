# CMake Parser

`ros_build_assistant` comes with a built-in CMake parser. This parser is able to provide a very high level of intelligence and can be used for other reasons.
The `cmake` module contains two functions which can be used to create an AST (Abstract Syntax Tree) given a `cmakelist.txt`. Your code can then manipulate the AST 
to output a new cmake file. This makes advanced code analysis possible for your tools. It also provides a building block for our intelligent cmake editing features possible.

## Example Usage