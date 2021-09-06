from collections import Counter
import re

from mir_sys.utils.generate_fingerprint import FingerprintGenerator
from mir_sys.utils.custom_base64 import NumBase64
from mir_sys.utils.util_classes import FingerprintSim, hamming_distance
from mir_sys.elasticsearch.queries import Queries

MAX_BIT = 24


class Retriever:

    MAX_NUM_BLOCK = 5
    THRESHOLD = 0.1

    def __init__(self):
        self.fingerprints = None
        self.query_hash_table = dict()

    def get_fingerprint(self, sample_or_dir):
        self.fingerprints = FingerprintGenerator.generate_fingerprint(sample_or_dir)

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
            rel_fingerprints = FingerprintSim.create_rel_fingerprints(fingerprint)
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

    # def make_positions_fingerprint(self) -> dict:
    #     """
    #     work with positions to make dict for make range fingerprint before and after
    #     :return:
    #     """
    #     positions = dict()
    #     length = len(self.fingerprints)
    #     reversed_fingerprints = list(reversed(self.fingerprints))
    #     for each in set(self.fingerprints):
    #         first_index, last_index = self.fingerprints.index(each), length - reversed_fingerprints.index(each) -1
    #         if first_index == last_index:
    #             positions[each] = (first_index, length-(first_index+1))
    #         else:
    #             positions[each] = (first_index, last_index, length-(first_index+1), length-(last_index+1))
    #     return positions

    def make_positions_fingerprint(self) -> list:
        """
        work with positions to make dict for make range fingerprint before and after
        :return:
        """
        positions = list()
        length = len(self.fingerprints)
        for i in range(length):
            positions.append((i, length-i-1))
        return positions

    def get_min_position(self) -> dict:
        """
        find the minimum offset for search in elastic
        """
        positions = dict()
        for each in self.query_hash_table:
            positions.update({each: self.fingerprints.index(each)})
        return positions

    def mack_regex(self) -> str:
        """
        :return: regex
        """
        fingerprint_regex_dict = self.make_regex_dict()
        range_list = self.make_positions_fingerprint()

        regex = r"(?=((.{4})*("
        for i in range(len(self.fingerprints)):
            regex += r".{}{}.{}|".format(str({range_list[i][0] * 4}),
                                         fingerprint_regex_dict[self.fingerprints[i]],
                                         str({range_list[i][1] * 4}))
        regex.rstrip("|")
        regex += r")(.{4})*))"
        return regex

    @classmethod
    def find_matches_in_song(cls, song_fingerprint: str, regex: str) -> list:
        """
        find all matches in a song_fingerprint
        :param song_fingerprint:
        :param regex:
        :return: a list of matches
        """
        results = re.findall(regex, song_fingerprint)
        return [each[2] for each in results]

    def second_scorer(self, songs: list):
        """
        score songs with their positions
        :param songs: ids
        :return: sorted songs
        """
        min_pos = self.get_min_position()
        return Queries.score_songs(songs, min_pos)

    def search_in_block(self, songs: list):
        """
        management for search in block
        :param songs: ids
        :return: if find match return song id else return None
        """
        sorted_songs = self.second_scorer(songs)
        regex = self.mack_regex()
        fingerprint = "".join(self.fingerprints)
        for song in sorted_songs:
            if self.is_match(song["_source"]["fingerprint"], regex, fingerprint):
                return song["_id"]
        return None

    @classmethod
    def is_match(cls, song_fingerprint: str, regex: str, fingerprint: str) -> bool:
        """
        :param song_fingerprint:
        :param regex:
        :param fingerprint:
        :return: is match or not
        """
        results = cls.find_matches_in_song(song_fingerprint, regex)
        for each in results:
            if cls.hamming_distance(each, fingerprint) < cls.THRESHOLD:
                return True
        return False

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


