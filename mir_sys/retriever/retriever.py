from mir_sys.utils.generate_fingerprint import FingerprintGenerator
from mir_sys.utils.custom_base64 import NumBase64
from mir_sys.elasticsearch.queries import Queries
import itertools

MAX_BIT = 24


class Retriever:
    CHANGE_INDEX_LIST = [x for x in itertools.combinations(range(MAX_BIT), 1)] + \
                        [x for x in itertools.combinations(range(MAX_BIT), 2)]

    def __init__(self):
        self.fingerprints = None
        self.query_hash_table = dict()

    def get_fingerprint(self, sample_or_dir):
        self.fingerprints = FingerprintGenerator.generate_fingerprint(sample_or_dir)

    @classmethod
    def create_rel_fingerprints(cls, fingerprint: str) -> list:
        """
        create rel_fingerprints with maximum 2 hamming_distance for a fingerprint
        :param fingerprint:
        :return: a list of rel_fingerprints
        """
        rel_fingerprints = set()
        binary_fingerprint = NumBase64.decode_to_binary(fingerprint)
        for index in cls.CHANGE_INDEX_LIST:
            new = str().join([str(0 ** int(binary_fingerprint[i])) if i in index else binary_fingerprint[i]
                              for i in range(len(binary_fingerprint))])
            rel_fingerprints.add(NumBase64.encode_binary_to_base64(new))
        return list(rel_fingerprints)

    @classmethod
    def get_fingerprint_songs(cls, fingerprint: str, rel_fingerprints: list) -> list:
        """
        :param fingerprint:
        :param rel_fingerprints:
        :return: return a list of songs
        """
        fingerprints_query = rel_fingerprints + [fingerprint]
        results = Queries.search_ids(fingerprints_query, "fingerprints")
        songs = set()
        for each in results:
            songs.update(set(each['songs']))
        return list(songs)

    def fill_hash_table(self):
        """
        create hast table for query
        """
        fingerprint_set = set(self.fingerprints)
        for fingerprint in fingerprint_set:
            rel_fingerprints = self.create_rel_fingerprints(fingerprint)
            songs = self.get_fingerprint_songs(fingerprint, rel_fingerprints)
            self.query_hash_table[fingerprint] = {"rels": rel_fingerprints, "songs": songs}