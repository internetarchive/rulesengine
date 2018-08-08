# XXX This is a simple implementation of a SURT library and not meant to be
# authoratitive, as something doubtless already exists

class Surt(object):
    """Represents a surt broken down into its component parts."""

    def __init__(self, surt):
        """Attempts to parse a surt string into its component parts."""
        self._surt = surt
        try:
            self.protocol, surt = surt.split('://(')
        except ValueError:
            self.protocol = surt
            surt = ''

        try:
            self.domain, surt = surt.split('/', 1)
        except ValueError:
            self.domain = surt
            surt = ''

        try:
            self.path, surt = surt.split('?')
        except ValueError:
            self.path = surt
            self.query = ''
            surt = ''

        try:
            self.query, self.hash = surt.split('#')
        except ValueError:
            if surt != '':
                self.query = surt
            self.hash = ''
            surt = ''

        if self.path:
            self.path_parts = self.path.split('/')
            self.path_parts = [part for part in self.path_parts if part != '']
        else:
            self.path_parts = []

        if self.domain:
            self.domain_parts = self.domain.replace(')', '').split(',')
            self.domain_parts = [
                part for part in self.domain_parts if part != '']
        else:
            self.domain_parts = []

        self.parts = []
        self.parts.append(self.protocol + '://(')
        for domain_part in self.domain_parts:
            self.parts.append('{},'.format(domain_part))
        self.parts[-1] = '{})'.format(self.parts[-1])
        for path_part in self.path_parts:
            self.parts.append('/{}'.format(path_part))
        self.parts.append(self.query)
        self.parts.append(self.hash)
        self.parts = [part for part in self.parts if part != '']

    def __str__(self):
        return self._surt
