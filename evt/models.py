class Line(object):
    def __init__(
        self, data, source, description=None, color=None, min=None,
        max=None, mean=None, continuum=None
    ):
        self.data = data
        self.source = source
        self.description = description
        self.color = color
        self.min = min
        self.max = max
        self.mean = mean
        self.continuum = continuum
