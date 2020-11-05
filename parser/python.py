from parser.abstract_file_description import AbstractFileDescription
import ast

class PythonFileDescription(AbstractFileDescription):

    def __init__(self, filename):
        self.backend = None 
        self.dependencies = set()
        self.filename = filename
    
    def _process_import_list(self, imports):
        dependencies = []
        packages = self.backend.get_package_list()
        for library in imports:
            if isinstance(library, ast.alias):
                library = library.name
            submodules = library.split(".")
            if submodules[0] in packages:
                dependencies.append(submodules[0])
        return dependencies

    def _parse_dependencies(self, filename):
        dependencies = []
        with open(filename) as f:
            file_ast = ast.parse(f.read())
            for node in ast.walk(file_ast):
                if isinstance(node, ast.Import):
                    dependencies += self._process_import_list(node.names)
                if isinstance(node, ast.ImportFrom):
                    if node.level > 0:
                        # Relative imports always refer to the current package.
                        continue
                    try:
                        dependencies += self._process_import_list([node.module])
                    except:
                        pass

        return set(dependencies)

    def get_dependencies(self):
        if len(self.dependencies) > 0:
            return self.dependencies
        self.dependencies = self._parse_dependencies(self.filename)
        return self.dependencies