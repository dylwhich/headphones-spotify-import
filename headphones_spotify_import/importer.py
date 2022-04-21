#!/usr/bin/env python3
######################################################
#
# Script created by DatScreamer.
# Updated and packaged by dylwhich
#
#
# Prerequisites:
#   Exportify CSV file named all.csv (https://rawgit.com/watsonbox/exportify/master/exportify.html)
#   Headphones with enabled API (Settings>Web Interface>API>Enable API) (https://github.com/rembo10/headphones)
#   Python (Hasn't been tested on any version lower than 3.62) (https://www.python.org/)
#   Python Requests (May require pip to install on windows, setup is easiest on linux in my opinion.) (http://docs.python-requests.org/en/master/user/install/))
#   Colorama (pip install colorama) https://pypi.python.org/pypi/colorama
# 
# Instructions:
#   1. Open Spotify (I used the desktop client) and create a new playlist with all the music you want to download. I went into "Songs" (Spotify>Songs) and selected everything with Ctrl+A then dragged the selection to the playlist in the sidebar.
#   2. Open your web browser and go to https://rawgit.com/watsonbox/exportify/master/exportify.html. Log in with your Spotify account and click export on your desired playlist.
#   3. Move the .csv file that you just downloaded to the same folder as importer.py and make sure it's named "all.csv"
#   4. Download and install Python, and Python Requests from the links in Prerequisites.
#   5. Install Headphones on whatever device you like, as long as it's on the same network as you are running the script on. If Headphones seemingly hasnt installed correctly and the webpage won't load you may need to edit the "config.ini" and change the host gateway (or whatever it's called.) from "localhost" to "0.0.0.0". This allows for headphones to run and be accessable on the network rather than just the local machine.
#   6. Setup Headphones. Go into the settings and configure your download settings, search provider settings, quality settings, etc...
#   7. Enable the API on Headphones. Go to Settings>Web Interface and enable the API.
#   8. Generate an API key from above webpage. And set your host and api key below.
#   9. You may need to use a Mirror domain for Musicbrainz if the musicbrainz searching is taking extended periods of time. If this is the case you can change it via Settings>Advanced Settings. I use the folling settings: Musicbrainz Mirror: Custom | Host: musicbrainz-mirror.eu | Port: 5000 | Required Authentication: No (unchecked) | Sleep Interval: 1
#   10. Am I missing anything? Lol. Don't think so. Let me know if you need help though.
#   11. Open terminal/command-line and navigate to the folder where all.csv and inporter.py are located.
#   12. Run this file. (importer.py)
#   13. Wait. It may take a really long time to complete the script, depending on your music library size.
######################################################'

import csv
import sys
import re
from os import PathLike
from typing import Optional
from .album import Album, Track

import requests

try:
    # Optional since it's only needed for win32
    import colorama
except ImportError:
    colorama = None

# Color escape codes
start = "\033[0;0m"
error = "\033[1;31m"
success = "\033[1;32m"
warning = "\033[1;33m"


def clean_str(value):
    return re.sub(r"[^A-Za-z0-9 -]", "", value).strip()


def format_unordered_list(values, *, char="*", newline="\n", indent: int = 0):
    indents = " " * (indent * 2 + 1)
    return newline.join(("{indents}{char} {value}".format(indents=indents, char=char, value=str(value)) for value in values))


def get_min_tracks_filter(min_tracks: int) -> callable:
    return lambda album: album and len(album.tracks) >= min_tracks


class Importer:
    def __init__(self, url: str, apikey: str, prompt: bool = True, color: bool = True, prompt_albums: bool = True):
        """
        Initialize a new importer for the given server
        :param url:
        :param apikey:
        :param prompt:
        :param color:
        :param prompt_almusm:
        """
        self.url = url
        self.apikey = apikey
        self.color = color
        self.prompt = prompt
        self.prompt_albums = prompt_albums
        self.__colorama_initialized = False

    def _init_colorama(self):
        if not self.__colorama_initialized:
            self.__colorama_initialized = True

            if colorama:
                colorama.init()

    def debug(self, msg: str):
        self._init_colorama()
        print(start + msg)

    def info(self, msg: str):
        self._init_colorama()
        print(start + msg)

    def success(self, msg: str):
        self._init_colorama()
        print(success + msg)

    def warn(self, msg: str):
        self._init_colorama()
        print(warning + msg)

    def error(self, msg: str):
        self._init_colorama()
        print(error + msg)

    def prompt_input(self, prompt, default=None):
        response = ""
        if self.prompt:
            while not response:
                response = input(prompt)

                if not response and default:
                    response = default
            return response
        else:
            raise RuntimeError("Required value: {prompt}".format(prompt=prompt))

    def prompt_continue(self, prompt, force=False):
        response = ""
        if self.prompt or force:
            while not response or response.lower()[0] not in ('y', 'n'):
                response = input(prompt)
            if response.lower() == "y":
                return True
            else:
                return False
        else:
            return True

    def headphones_find_album_id(self, album_info: Album) -> str:
        """
        Comminucates with headphones to search for the given album and return the first matching album ID.
        :param album_info: A dict describing the album, as returned by `import_playlist`.
        :return: The album ID as a string, or `None` if the album was not found.
        """
        payload = {
            "cmd": "findAlbum",
            "name": str(album_info),
            "apikey": self.apikey,
        }

        response = requests.get(self.url + "/api", params=payload)
        response.raise_for_status()

        matches = response.json()
        for match in matches:
            # Match fields:
            # * uniquename (artist)
            # * title (album)
            # * id (artist)
            # * albumid (album)
            # * url (artist)
            # * albumurl (album)
            # * score
            # * date
            # * country
            # * formats
            # * tracks (album)
            # * rgid (release group?)
            # * rgtype (release group?)

            match_title = clean_str(match["title"]).lower()
            match_artist = clean_str(match["uniquename"]).lower()
            album_title = clean_str(album_info.name).lower()
            album_artists = clean_str(album_info.artists).lower()

            name_match = (
                    match_title == album_title
                    or match_title.startswith(album_title)
            )
            artist_match = (
                    match_artist in album_artists
                    or any((clean_str(track.artist).lower() == match_artist for track in album_info.tracks))
            )

            if name_match and artist_match:
                return match["albumid"]

        self.warn(
            "Warning. Album '{}' not found after searching {} possible matches.".format(payload["name"], len(matches))
        )
        return None

    def headphones_add_album(self, album_id: str):
        """
        Communicates with headphones to download an album by its ID
        :param album_id: The ID of the album, as defined by its musicbrainz
        :return:
        """

        payload = {
            "cmd": "addAlbum",
            "id": album_id,
            "apikey": self.apikey,
        }

        response = requests.get(self.url + "/api", params=payload)
        response.raise_for_status()

    def headphones_queue_album(self, album_id: str, new: bool = True, lossless: bool = True):
        """
        Communicates with headphones to queue an album (i.e. mark it as wanted and search for it) by `album_id`
        :param album_id:
        :param new: Optional. Whether to look for new versions. Defaults to `True`.
        :param lossless: Optional. Whether to only search for lossless versions. Defaults to `True`.
        :return:
        """

        payload = {
            "cmd": "queueAlbum",
            "id": album_id,
            "new": new,
            "lossless": lossless,
            "apikey": self.apikey,
        }

        response = requests.get(self.url + "/api", params=payload)
        response.raise_for_status()

    def import_playlist(self, files: "list[PathLike]", queue: bool = False, lossless: bool = True, min_tracks: Optional[int] = 1):
        """
        Imports and optionally queues a playlist.
        :param files: A list of paths to CSV playlist files
        :param queue: If `True`, albums will be queued after they are imported.
        :param lossless: If `True`, only lossless albums will be added when queued. Defaults to `True`.
        :param min_tracks: If set, a track from this album must be included at least `min_tracks` times to be included.
        :return: A dictionary summarizing the actions that were taken.
        """

        if not files:
            files = [self.prompt_input("Playlist File [all.csv]: ", default="all.csv")]

        if not self.url:
            self.url = self.prompt_input("Headphones URL [http://jellyfin:8181]: ", default="http://jellyfin:8181")

        if not self.url.startswith("http"):
            self.url = "http://" + self.url

        if not self.apikey:
            self.apikey = self.prompt_input("Headphones API key: ")

        self.info("Caution: This may take a very long time to complete, Depending on your music library size.")

        self.info("Loading {} playlist file(s):".format(len(files)))
        self.info("files: {}".format(files))
        self.info(format_unordered_list(files))

        # Load the album and track info from the playlist file
        albums = self.load_playlist_albums(*files)

        self.info("About to be performed:")

        self.info(" * Search for {} albums".format(len(albums)))

        if not self.prompt_continue("Continue? (y/n) "):
            sys.exit(1)

        albums_to_add = []
        filters = []

        if min_tracks > 1:
            filters.append(get_min_tracks_filter(min_tracks))
        elif self.prompt_albums:
            filters.append(
                lambda a: self.prompt_continue("Add album '{}'? (y/n) ".format(a))
            )

        # Print each album with the tracks we want from it, and maybe allow the user to confirm it
        self.info("Albums to search:")
        self.info("===========")
        for album in albums:
            self.info("{}".format(album))
            self.info(" Tracks:")
            self.info(format_unordered_list(album.tracks))

            if all((f(album) for f in filters)):
                self.success(" Will be added!")
                albums_to_add.append(album)
            else:
                self.info(" Will be skipped!")
                album.status = "Skipped"
        self.info("===========")

        self.info("Searching musicbrainz for album IDs...")
        for album in albums_to_add:
            try:
                # Note that here the returned album_id may still be `None`. We will skip those later.
                album_id = self.headphones_find_album_id(album)
                album.musicbrainz_id = album_id

                if album_id:
                    self.success("Mapped {album} to album ID: {album_id}".format(album=album, album_id=album_id))
                else:
                    self.warn("Could not find album_id for {}".format(album))
                    album.status = "Error: Could not find album_id"

            except requests.exceptions.RequestException as e:
                album.status = "Error: Could not find ID: " + str(e.args)
                self.error("Error. While searching musicbrainz for {album}: {err}".format(err=e.args, album=album))

        for album in albums_to_add:
            if not album.musicbrainz_id:
                self.warn("Skipping {} due to missing album_id".format(album))
                continue

            self.info("Adding album {}...".format(album))
            try:
                self.headphones_add_album(album.musicbrainz_id)
                album.status = "Added"
                self.success("Added!")
                if queue:
                    self.info("Queueing album")
                    self.headphones_queue_album(album.musicbrainz_id, lossless=lossless)
                    album.status = "Queued"
            except requests.exceptions.RequestException as e:
                action = "adding"

                if album.status == "Added":
                    # This means we failed queueing
                    action = "queueing"
                    album.status = "Error: Not queued"
                else:
                    album.status = "Error: Not added"

                self.error(
                    "Error. While {action} {album} to headphones: {err}".format(
                        err=e.args, action=action, album=album
                    )
                )

        queued = sum((album.status == "Queued" for album in albums))
        added = sum((album.status == "Added" for album in albums))
        skipped = sum((album.status == "Skipped" for album in albums))
        to_add_count = len(albums_to_add)
        total = len(albums)

        summary = dict(queued=queued, added=added, skipped=skipped, to_add_count=to_add_count, total=total)

        self.info(
            "Queued {queued} / Added {added} / {to_add_count} albums (skipped {skipped} / {total})"
            .format_map(summary)
        )

        for album in albums:
            status_text = "{album}: {status}".format(album=album, status=album.status)
            if album.status == "Added":
                self.success(status_text)
            elif album.status == "Skipped":
                self.warn(status_text)
            else:
                self.error(status_text)

        return summary

    def load_playlist_albums(self, *files, skip_errors=False) -> "list[Album]":
        """
        Loads the CSV playlist at each path in `file` and returns a list of dicts describing albums and the desired tracks.
        :param files: The path to a CSV playlist.
        :param skip_errors: If `True`, will continue loading files after an error in one.
        :return: A list of album_info. Each has `artist_name`, `album_name`, `album_artist_names`, and `track_names`.
        """
        found_albums = {}

        for file in files:
            self.info("Loading playlist file '{}'...".format(file))
            try:
                with open(file) as f:
                    csv_reader = csv.DictReader(f)

                    # CSV FIELDS (*: used currently)
                    # Index: Name
                    # ----------------
                    #  0: "Track URI"
                    #  1: "Track Name"  *
                    #  2: "Artist URI(s)"
                    #  3: "Artist Name(s)" *
                    #  4: "Album URI"
                    #  5: "Album Name" *
                    #  6: "Album Artist URI(s)"
                    #  7 "Album Artist Name(s)" *
                    #  8: "Album Release Date"
                    #  9: "Album Image URL"
                    # 10: "Disc Number"
                    # 11: "Track Number"
                    # 12: "Track Duration (ms)"
                    # 13: "Track Preview URL"
                    # 14: "Explicit"
                    # 15: "Popularity"
                    # 16: "Added By"
                    # 17: "Added At"

                    for row in csv_reader:
                        track_name = row["Track Name"]
                        artist_name = row["Artist Name(s)"]

                        album_name = row["Album Name"]
                        album_artist_names = row["Album Artist Name(s)"]
                        album_release_date = row["Album Release Date"]
                        album_id = row["Album URI"]

                        key = album_id #(album_artist_names, album_name)
                        if key not in found_albums:
                            found_albums[key] = Album(album_name, album_artist_names, album_release_date)

                        album_info = found_albums[key]
                        album_info.add_track(Track(track_name, artist_name))
            except KeyError as e:
                self.error("Error. Incorrectly formatted playlist in file '{}'?: {}".format(file, e.args))
                if not skip_errors:
                    raise
            except IOError as e:
                self.error("Error. Could not load playlist '{}': {}".format(file, e.args))
                if not skip_errors:
                    raise

        total_tracks = sum((len(album_info.tracks) for album_info in found_albums.values()))
        self.info("Loaded {} albums for {} songs from {}".format(len(found_albums), total_tracks, files))

        return list(found_albums.values())


__all__ = ["Importer"]
