class NewRelease:

    def __init__(self, artist, album, url):
        self.artist = artist
        self.album = album
        self.url = url

    def __str__(self):
        return f'{self.artist} - {self.album}({self.url})'

    def __eq__(self, other):
        return self.album == other.album and self.artist == other.artist

    def __hash__(self):
        return hash(self.artist + self.album)

    def to_html(self):
        return f'{self.artist} - <a href="{self.url}">{self.album}</a>'
