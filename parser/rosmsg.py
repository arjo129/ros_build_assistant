from parser.abstract_file_description import AbstractFileDescription
import ast

# Taken from: http://wiki.ros.org/msg
BUILT_IN_TYPES = ["bool", "int8", "uint8", "int16", "uint16", "int32", "uint32", 
                "int64", "uint64", "float32", "float64", "string", "time", "duration"]

class Ros1MsgFileDescription(AbstractFileDescription):

    def __init__(self, filename):
        self.backend = None 
        self.dependencies = set()
        self.filename = filename

    def _parse_dependencies(self, filename):
        """ Hack job parser for message files """
        dependencies = []
        all_packages = self.backend.get_package_list()
        with open(filename) as f:
            lineno = 0
            for line in f:
                lineno += 1
                items = line.split(" ")
                if len(items) == 0:
                    continue
                if "#" in items[0]: #comment or malformatted line.
                    continue
                if items[0] in BUILT_IN_TYPES:
                    continue
                if "/" not in items[0]:
                    print ("Uh oh looks like a malformatted line...")
                    print ("Error: In file "+filename)
                    print ("Line: "+str(lineno))
                    print ("\t"+line)
                    print ("\tWas unable to determine the package type")
                    #TODO: Should probably terminate the process
                    continue
                
                package_details = items[0].split("/")

                if len(package_details) < 1:
                    print ("Uh oh looks like a malformatted line...")
                    print ("Error: In file "+filename)
                    print ("Line: "+str(lineno))
                    print ("\t"+line)
                    print ("\tWas unable to determine the package type")

                package_name = package_details[0]
                
                if package_name not in all_packages:
                    print ("Warning: In file "+filename)
                    print ("Line: "+str(lineno))
                    print ("\tFound dependency "+package_name+" which does not seem to be installed on the system")

                # TODO: This is a good place to add an error check also
                dependencies.append(package_name)

        return set(dependencies)

    def get_dependencies(self):
        if len(self.dependencies) > 0:
            return self.dependencies
        self.dependencies = self._parse_dependencies(self.filename)
        return self.dependencies