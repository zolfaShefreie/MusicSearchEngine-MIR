from collections import Counter
import itertools

from mir_sys.utils.generate_fingerprint import FingerprintGenerator
from mir_sys.utils.custom_base64 import NumBase64
from mir_sys.elasticsearch.queries import Queries

MAX_BIT = 24


class Retriever:
    CHANGE_INDEX_LIST = [x for x in itertools.combinations(range(MAX_BIT), 1)] + \
                        [x for x in itertools.combinations(range(MAX_BIT), 2)]

    MAX_NUM_BLOCK = 5

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

    def make_block_search(self) -> list:
        """
        set score for songs based on repeat in fingerprint list and then block them
        :return: block list
        """
        songs = [song for fingerprint in self.fingerprints
                 for song in self.query_hash_table[fingerprint]['songs']]
        song_score = dict(Counter(songs))

        # initial block list
        blocks = [list() for i in range(self.MAX_NUM_BLOCK)]

        for song in song_score:
            score = song_score[song]/len(self.fingerprints)
            for i in range(1, self.MAX_NUM_BLOCK+1):
                if score < ((1/self.MAX_NUM_BLOCK) * i):
                    blocks[i].append(song)

        return blocks

    def make_regex_dict(self) -> dict:
        """
        :return:
        """
        fingerprint_regex = dict()
        for fingerprint in self.query_hash_table:
            regex = r"".join([each + "|" for each in self.query_hash_table[fingerprint]]).rstrip("|")
            fingerprint_regex[fingerprint] = r"({}|{})".format(fingerprint, regex)
        return fingerprint_regex

    def make_positions_fingerprint(self) -> dict:
        """
        work with positions to make dict for make range fingerprint before and after
        :return:
        """
        positions = dict()
        length = len(self.fingerprints)
        reversed_fingerprints = list(reversed(self.fingerprints))
        for each in set(self.fingerprints):
            first_index, last_index = self.fingerprints.index(each), length - reversed_fingerprints.index(each) -1
            if first_index == last_index:
                positions[each] = (first_index, length-(first_index+1))
            else:
                positions[each] = (first_index, last_index, length-(first_index+1), length-(last_index+1))
        return positions

    def mack_regex(self) -> str:
        """
        :return: regex
        """
        fingerprint_regex_dict = self.make_regex_dict()
        range_dict = self.make_positions_fingerprint()

        regex = r"(.{4})*("
        for each in range_dict:
            if len(range_dict[each]) == 2:
                regex += r"((.{}){}{}(.{}){}))|".format(str({4}), range_dict[0], fingerprint_regex_dict[each], str({4}),
                                                        range_dict[1])
            elif len(range_dict[each]) == 4:
                regex += r"((.{}){}{}(.{}){}))|" .format(str({4}), fingerprint_regex_dict[each],
                                                         "{" + "{}, {}".format(range_dict[0], range_dict[1]) + "}",
                                                         str({4}),
                                                         "{" + "{}, {}".format(range_dict[2], range_dict[3]) + "}")
        return regex

    def search_in_songs(self, songs: list):
        pass

    @staticmethod
    def hamming_distance(match_fingerprint: str, query_fingerprint: str):
        """
        :param match_fingerprint:
        :param query_fingerprint:
        :return: return hamming distance of two fingerprint
        """
        match_binary = NumBase64.decode_to_binary(match_fingerprint)
        query_binary = NumBase64.decode_to_binary(query_fingerprint)
        xor = bin(int(match_binary, 2) ^ int(query_binary, 2)).lstrip("0b")
        distance = 0
        for each in xor:
            if each == "1":
                distance += 1
        return distance/len(query_binary)

    def retrieve(self, sample_or_dir):
        pass


