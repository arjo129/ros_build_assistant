import clang.cindex
from parser.abstract_file_description import AbstractFileDescription

class CppFileDescription(AbstractFileDescription):

    def __init__(self, filename):
        self.includes = get_includes(filename)
        self.backend = None 
    
    def get_dependencies(self):
        ros_headers = set(self.backend.get_exported_headers())
        included = set(self.includes)
        packages = []
        for header in included:
            if header in ros_headers:
                package = self.backend.get_package_from_header(header)
                packages.append(package)
        return packages

    def get_system_dependencies(self):
        pass

def _parse_ast(node, typename):
    """ 
    Recursively parse and find includes
    TODO: Add forward declaration
    """
    res = []
    if node.kind == clang.cindex.CursorKind.INCLUSION_DIRECTIVE:
        res.append(node.spelling)
    # Recurse for children of this node
    for c in node.get_children():
        res += _parse_ast(c, typename)
    return res


def get_includes(filename):
    index = clang.cindex.Index.create()
    tu = index.parse(filename, options=1|2|64|1024)
    includes = _parse_ast(tu.cursor, None)
    return includes




