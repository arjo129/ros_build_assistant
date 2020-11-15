from parser.cpp import CppFileDescription
from parser.python import PythonFileDescription
from parser.rosmsg import Ros1MsgFileDescription

parser_types = {
    ".cpp": CppFileDescription,
    ".cxx": CppFileDescription,
    ".CPP": CppFileDescription,
    ".C": CppFileDescription,
    ".hpp": CppFileDescription,
    ".h": CppFileDescription,
    ".py": PythonFileDescription,
    ".msg": Ros1MsgFileDescription
}

class GenericFileHandler:
    def __init__(self, backend):
        self.backend = backend

    def get_dependencies(self, filename):
        for file_type in parser_types:
            if filename.endswith(file_type):
                parser = parser_types[file_type](filename)
                parser.set_backend(self.backend)
                return parser.get_dependencies()
        print ("Warning: Ignoring "+filename+"as no file handler has been registered")
        return []