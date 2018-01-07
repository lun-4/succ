class Route:
    """Defines a simple route."""
    def __init__(self, method, path):
        self.method = method
        self.path = path

    def __repr__(self):
        return f'Route({self.method}, {self.path!r})'
