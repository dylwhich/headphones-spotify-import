import argparse

parser = argparse.ArgumentParser(
    description="Collects albums from spotify playlists and imports them to a headphones server",
    epilog="To generate CSV playlists from spotify, see https://github.com/dylwhich/headphones-spotify-import#Usage"
)

parser.add_argument(
    "--url", "-u",
    type=str,
    help="The base URL of headphones, e.g. headphones:8181 or https://headphones.example.com. "
         "If not given, it will be prompted for, unless `-y` is selected, in which case `headphones:8181` is used."
)
parser.add_argument(
    "--api-key", "-k",
    type=str,
    help="The headphones API key. If not set, it will be prompted for unless `-y` is selected."
)
parser.add_argument("--color", default="yes", choices=["yes", "no"], help="Whether to color the output. Default 'yes'")
parser.add_argument("--yes", "-y", action="store_true", default=False, help="Skip all prompts and import everything.")
parser.add_argument(
    "--yes-albums", "-a",
    action="store_true",
    default=False,
    help="Skip prompts for each album. Assumed with --min-tracks"
)
parser.add_argument("--queue", "-q", action="store_true", default=False, help="Queue all albums after adding them.")
parser.add_argument("--lossless", "-l", action="store_true", default=False, help="When queueing, only search lossless.")
parser.add_argument(
    "--min-tracks", "-m",
    type=int,
    default=1,
    help="If specified, albums will only be added when at least this many of their songs are included in playlists"
)
parser.add_argument("files", nargs="+", metavar="PLAYLIST_CSV", help="One or more paths to CSV playlist files")
