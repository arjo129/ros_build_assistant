class AbstractFileDescription:

    def __init__(self):
        self.backend = None
        
    def get_dependencies(self):
        pass

    def set_backend(self, backend):
        self.backend = backend
        