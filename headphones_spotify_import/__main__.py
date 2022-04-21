import sys
import traceback

from .args import parser
from .importer import Importer


def main():
    try:
        params = parser.parse_args()

        importer = Importer(params.url, params.api_key, prompt=not params.yes, color=(params.color == "yes"), prompt_albums=not (params.yes or params.yes_albums))

        importer.import_playlist(params.files, queue=params.queue, lossless=params.lossless, min_tracks=params.min_tracks)

        return 0
    except Exception as e:
        print("Fatal error: {}".format(e.args))
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
