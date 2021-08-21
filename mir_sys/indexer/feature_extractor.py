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
    def save_fingerprint(cls, song_id: str, fingerprints: list):
        """
        :param fingerprints:
        :param song_id:
        :return:
        """
        complete_fingerprints = "".join(fingerprints)
        unique_fingerprints = set(fingerprints)
        cls.queries.update_obj(obj_id=song_id, index_name="songs",
                               obj={'fingerprint': complete_fingerprints})
        cls.queries.update_song_list(list(unique_fingerprints), song_id)

    @classmethod
    def run(cls):
        ids, seen = cls.get_ids()
        if not seen:
            cls.queries.set_seen_songs(ids)
        Downloader.download_manager(ids)
        for song_id in ids:
            path = f"{DOWNLOAD_PATH}{song_id}.wav"
            if os.path.exists(path):
                cls.save_fingerprint(song_id, FingerprintGenerator.generate_fingerprint(dir_or_samples=path))
