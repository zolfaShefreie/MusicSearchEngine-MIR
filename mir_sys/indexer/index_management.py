from multiprocessing import Process

from mir_sys.indexer.explore_artist import ArtistExplorer
from mir_sys.indexer.explore_songs import SongExplorer
from mir_sys.indexer.feature_extractor import FeatureExtractor


def management():
    """
    the core of indexer for manage the 3 modules to crawl and index data
    """
    artist_explorer_process = Process(target=ArtistExplorer.run)
    artist_explorer_process.start()

    song_counter = 0
    feature_counter = 0

    while True:
        pass

