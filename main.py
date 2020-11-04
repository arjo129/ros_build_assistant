import sys
from parser.file_parser import GenericFileHandler
from backends.ros1.ros1_backend import Ros1Backend

if __name__ == "__main__":
    file_handler = GenericFileHandler(Ros1Backend())
    print ("Analyzing workspace")
    print ("Analyzing file", sys.argv[1])
    print (file_handler.get_dependencies(sys.argv[1]))