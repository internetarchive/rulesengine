from urlcanon import parse_url


class Surt(object):
    """Represents a SURT broken down into its component parts."""

    def __init__(self, surt):
        """Attempts to parse a SURT string into its component parts.

        Arguments:
        surt -- A SURT
        """
        self.surt = surt

        # Pull out the protocol
        try:
            self.protocol, surt = surt.split('://(', 1)
        except ValueError:
            # If there's no protocol separator, then assume we've received
            # only the protocol (e.g: `Surt('http')`).
            self.protocol = surt
            surt = ''

        # Pull out the domain.
        try:
            self.domain, surt = surt.split(')', 1)
            self.closing_paren = True
        except ValueError:
            # If there's no path separator, we've received only the domain.
            self.closing_paren = False
            self.domain = surt
            surt = ''

        # The following only need to be done if we've received more than
        # just the domain.
        if self.closing_paren:
            # Pull out the path.
            try:
                self.path, surt = surt.split('?')
            except ValueError:
                # If there's no query string separator, we only have the path
                # left, potentially with a hash.
                self.path = surt
                self.query = ''
                surt = ''

            # Pull out the hash.
            try:
                if surt == '':
                    self.path, self.hash = self.path.split('#')
                else:
                    self.query, self.hash = surt.split('#')
            except ValueError:
                # If there's no hash separator, ensure that we capture the
                # query,then set the remainder of the surt and the hash to
                # empty strings.
                if surt != '':
                    self.query = surt
                self.hash = ''
                surt = ''
        else:
            self.path = ''
            self.query = ''
            self.hash = ''

        # Split the path into its component parts.
        if self.path != '':
            self.path_parts = self.path.split('/')
            # Splitting on / will leave an empty string as the first entry.
            if self.path_parts[0] == '':
                self.path_parts = self.path_parts[1:]
        else:
            self.path_parts = []

        # Split the domain into its component parts.
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
        if self.closing_paren:
            self.parts.append(')')
            for path_part in self.path_parts:
                self.parts.append('/{}'.format(path_part))
            if self.query:
                self.parts.append('?{}'.format(self.query))
            if self.hash:
                self.parts.append('#{}'.format(self.hash))
        self.parts = [part for part in self.parts if part != '']

    @classmethod
    def from_url(cls, url):
        """Returns broken-down SURT from a URL.

        Arguments:
        url -- The URL to SURTify.

        Returns:
        A SURT broken down into its parts.
        """
        return cls(parse_url(url).surt().decode('utf-8'))

    def __str__(self):
        return self.surt
