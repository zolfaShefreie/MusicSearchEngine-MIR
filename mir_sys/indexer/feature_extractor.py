import os

from mir_sys.elasticsearch.queries import Queries
from mir_sys.utils.audio_downloader import Downloader, DOWNLOAD_PATH
from mir_sys.utils.generate_fingerprint import FingerprintGenerator


class FeatureExtractor:
    queries = Queries()

    @classmethod
    def get_ids(cls) -> (list, int):
        """
        check for songs that should download
        :return: a list of ids and seen status
        """
        ids = cls.queries.get_unseen_songs()
        if not ids:
            return cls.queries.get_no_feature_songs(), True
        return ids, False

    @classmethod
    def run(cls):
        ids, seen = cls.get_ids()
        if not seen:
            cls.queries.set_seen_songs(ids)
        Downloader.download_manager(ids)
        for song_id in ids:
            path = f"{DOWNLOAD_PATH}{song_id}.wav"
            if os.path.exists(path):
                fingerprint_list = FingerprintGenerator.generate_fingerprint(dir_or_samples=path)
                #TODO save fingerprint
