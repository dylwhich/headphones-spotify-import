Headphones Spotify Import
=========================================================


Notice: Due to the fact that Headphones relies on Musicbrainz to find information (artists, albums), we cannot guarantee
that a song will be added to Headphones because of disparities between the Spotify and Musicbrainz databases. For
example, Spotify may have an album, but Musicbrainz may only have songs from that album as singles.

Headphones Spotify Import imports CSV playlists from spotify and automatically searches and adds them to a headphones
media server.

---------------------------------------------------------

Prerequisites
---------------------------------------------------------
1. [Headphones](https://github.com/rembo10/headphones) with enabled API (Settings -> Web Interface -> API -> Enable API)
2. A [Spotify](https://spotify.com) account.
3. [Python3.6+](https://www.python.org/)
4. [Poetry](https://python-poetry.org/) to manage dependencies, environments, and building / packaging.
5. (If not using Poetry) Python packages installed:
   * [requests](https://docs.python-requests.org/en/latest/user/install/#install). Install with `pip install requests`.
   * *(Optional, Windows-only)* [colorama](https://pypi.org/project/colorama/) for color text support.
   Install with `pip install colorama`.

---------------------------------------------------------

Installation
---------------------------------------------------------
1. Install python >= 3.6: https://www.python.org/downloads/
2. Install poetry: https://python-poetry.org/docs/#installation
3. Inside the repository root, run `poetry install` to install the project dependencies and set up the virtualenv.
4. To install globally, run `poetry build` to build the package, then install with
`pip install dist/headphones_spotify_import-0-2.0-py3-none-any.whl` (or `pip install dist/*.whl` for any version). You\may need `sudo` if
you attempt to install system-wide.
5. To skip global installation and use the virtualenv version, just run `poetry shell`. Once you're done, you can leave
the virtualenv shell with `exit`.
6. Now, you can run it with `headphones-spotify-import <args...>` or `python -m headphones_spotify_import <args...>`.
Run `headphones-spotify-import --help` to get a list of all options.

Usage
---------------------------------------------------------
1. Check that you have all the [prerequisites](#Prerequisites) first.
2. If you don't just want to export existing playlists, use your favorite spotify client to create a playlist (or
multiple playlists) with songs you want to export. Or, just Ctrl+A to select all songs and add them to a playlist.
3. Export your Spotify playlists to CSV files at https://rawgit.com/watsonbox/exportify/master/exportify.html.
Connect with your Spotify account, and click "export" on the desired playlists.
4. From the headphones web interface, enable the API from Settings -> Web Interface
5. Click "Generate" to generate an API key, and copy it.
6. [Install headphones-spotify-import](#Installation) if you haven't already.
7. Run `headphones-spotify-import`. If you provide no arguments, you will be prompted for the URL of the headphones
server, the headphones API key, and the path of a CSV playlist file. Once the playlists have been loaded, you will also
be prompted for each album. The `--yes-albums` or `-a` argument will automatically approve all albums, or you can use
`--min-tracks NUM` or `-m NUM` to automatically include any album with at least `NUM` tracks included in the playlists.
To automatically search for each album after adding, use `--queue` or `-q`.
8. To run fully automatically, use a command of the form 
`headphone-spotify-import -y -q -k <headphones api key> -u http://headphones.example.net:8181 playlist.csv`, which will
automatically import and search for any albums in `playlist.csv` without any user input required.
9. You may need to use a Mirror domain for Musicbrainz if the musicbrainz searching is taking extended periods of time.
If this is the case you can change it via Settings>Advanced Settings. I use the folling settings:
Musicbrainz Mirror: Custom | Host: musicbrainz-mirror.eu | Port: 5000 | Required Authentication: No (unchecked) | Sleep Interval: 1
10. Wait. It may take a really long time to complete the script, depending on your music library size.

Command-line Help
---------------------------------------------------------
```
usage: headphones-spotify-import [-h] [--url URL] [--api-key API_KEY]
                                 [--color {yes,no}] [--yes] [--yes-albums]
                                 [--queue] [--lossless]
                                 [--min-tracks MIN_TRACKS]
                                 PLAYLIST_CSV [PLAYLIST_CSV ...]

Collects albums from spotify playlists and imports them to a headphones server

positional arguments:
  PLAYLIST_CSV          One or more paths to CSV playlist files

optional arguments:
  -h, --help            show this help message and exit
  --url URL, -u URL     The base URL of headphones, e.g. headphones:8181 or
                        https://headphones.example.com. If not given, it will
                        be prompted for, unless `-y` is selected, in which
                        case `headphones:8181` is used.
  --api-key API_KEY, -k API_KEY
                        The headphones API key. If not set, it will be
                        prompted for unless `-y` is selected.
  --color {yes,no}      Whether to color the output. Default 'yes'
  --yes, -y             Skip all prompts and import everything.
  --yes-albums, -a      Skip prompts for each album. Assumed with --min-tracks
  --queue, -q           Queue all albums after adding them.
  --lossless, -l        When queueing, only search lossless.
  --min-tracks MIN_TRACKS, -m MIN_TRACKS
                        If specified, albums will only be added when at least
                        this many of their songs are included in playlists

To generate CSV playlists from spotify, see
https://github.com/dylwhich/headphones-spotify-import#Usage
```
