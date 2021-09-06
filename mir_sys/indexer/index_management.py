from multiprocessing import Process
import time

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
        if song_counter < 100:
            song = SongExplorer.run()
            # if there is no new artist and no query result
            if not artist_explorer_process.is_alive() and song == 0:
                song_counter += 1
                time.sleep(0.5)
            else:
                song_counter = 0

        if feature_counter < 100:
            feature = FeatureExtractor.run()
            # if there is no new artist or new song and no query result
            if not artist_explorer_process.is_alive() and song_counter >= 100 and feature == 0:
                feature_counter += 1
                time.sleep(0.5)
            else:
                feature_counter = 0

        if feature_counter >= 100 and song_counter >= 100:
            break
