from ytmusicapi import YTMusic
from django.conf import settings
import datetime

from mir_sys.utils.util_classes import CDict
from mir_sys.elasticsearch.queries import Queries


PATH = getattr(settings, 'MUSIC_BRAINS', {})['ARTIS_TOKEN_PATH']
EXPIRE_YEAR = getattr(settings, 'CHECK_ARTISTS_YEAR', 1)


class ARTIST_EXPLOREE:
    ytmusic = YTMusic()
    queries = Queries()

    @classmethod
    def search_and_get_ids(cls, term: str) -> list:
        """
        search in youtube music and get ids
        :param term:
        :return: a list of artist ids
        """
        try:
            # the second search has more results
            cls.ytmusic.search(term, filter="artists", limit=1000)
            results = cls.ytmusic.search(term, filter="artists", limit=1000)
            return [result['browseId'] for result in results]
        except:
            return list()

    @classmethod
    def create_artist_objs(cls, ids: list):
        """
        if id doesn't exist create a artist obj
        :param ids:
        :return:
        """
        objs = list()
        exist_objs = cls.queries.exist_ids(ids=ids, index_name="artists")
        for each in ids:
            if each not in exist_objs:
                objs.append({"id": each,
                             "data": {"last_check": (datetime.datetime.now() -
                                                     datetime.timedelta(days=365)).date().strftime("%Y-%m-%d")}})
        cls.queries.create_multi_objs(objs, "artists")

    @classmethod
    def run(cls):
        tokens = CDict(PATH)
        for each in tokens:
            if not tokens[each]:
                artist_ids = cls.search_and_get_ids("each")
                if artist_ids:
                    cls.create_artist_objs(artist_ids)
                tokens.update({each: True})
