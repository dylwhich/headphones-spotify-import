from datetime import date


class Track:
    def __init__(self, name, artist):
        self.name = name
        self.artist = artist

    def __str__(self):
        return "{artist} - {name}".format(name=self.name, artist=self.artist)


class Album:
    def __init__(self, name, artists, release_date):
        self.name = name
        self.artists = artists
        self.release_date = release_date

        try:
            self.release_year = date.fromisoformat(release_date).year
        except ValueError:
            self.release_year = release_date[:4]

        self.tracks = []

        self.status = None
        self.musicbrainz_id = None

    def add_track(self, track: Track):
        self.tracks.append(track)

    def __str__(self):
        return "{artists} - {name} ({year})".format(artists=self.artists, name=self.name, year=self.release_year)