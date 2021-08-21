from ytmusicapi import YTMusic
from django.conf import settings
import datetime


from mir_sys.elasticsearch.queries import Queries


EXPIRE_YEAR = getattr(settings, 'CHECK_ARTISTS_YEAR', 1)


class SongExplorer:
    ytmusic = YTMusic()
    queries = Queries()
    LIMITS = 10

    @staticmethod
    def get_date_year_ago():
        return (datetime.datetime.now() - datetime.timedelta(days=EXPIRE_YEAR * 365)).date().strftime("%Y-%m-%d")

    @classmethod
    def get_artist_videos(cls, artist_id: str) -> list:
        """
        :param artist_id:
        :return: a list of video ids
        """
        return_list = list()
        result = cls.ytmusic.get_artist(artist_id)
        return_list.extend([each.get('videoId', None)
                            for category in [result.get('songs', {}).get('results', []),
                                             result.get('videos', {}).get('results', [])]
                            for each in category if each.get('videoId', None)])
        albums = [each.get('browseId', None)
                  for category in [result.get('singles', {}).get('results', []),
                                   result.get('albums', {}).get('results', [])]
                  for each in category if each.get('browseId', None)]
        return_list.extend([each for album in albums for each in cls.get_album_videos(album)])
        return list(set(return_list))

    @classmethod
    def get_album_videos(cls, album_id: str) -> list:
        """
        :param album_id:
        :return:
        """
        results = cls.ytmusic.get_album(album_id).get('results', [])
        return list(set([each.get('videoId', None) for each in results if each.get('videoId', None)]))

    @classmethod
    def create_song_objs(cls, ids: list, artist_id: str):
        """
        if id doesn't exist create a songs obj
        :param ids:
        :param artist_id:
        :return:
        """
        objs = list()
        exist_objs = cls.queries.exist_ids(ids=ids, index_name="songs")
        for each in ids:
            if each not in exist_objs:
                objs.append({"id": each,
                             "data": {"artist": artist_id, "seen": False, "fingerprint": ""}})
        cls.queries.create_multi_objs(objs, "songs")

    @classmethod
    def update_artist_last_check(cls, artist_id: str):
        """
        set last_check to today date
        :param artist_id:
        :return:
        """
        cls.queries.update_obj(obj_id=artist_id, index_name="artists",
                               obj={'last_check': datetime.datetime.today().strftime("%Y-%m-%d")})

    @classmethod
    def run(cls):
        artists = cls.queries.get_expire_artists(cls.get_date_year_ago(), cls.LIMITS)
        for each in artists:
            cls.create_song_objs(ids=cls.get_artist_videos(each), artist_id=each)
            cls.update_artist_last_check(each)
