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
        # hold a copy of all values of a plot, doubled but this is the only way
        # the value can be accessed as there is no way you could read it
        # from the plot itself
        self.continuum = continuum
