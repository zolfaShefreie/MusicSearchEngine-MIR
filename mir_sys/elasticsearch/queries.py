from elasticsearch import Elasticsearch, helpers


class Queries:
    ES_CONN = Elasticsearch()

    # methods for all indices

    @classmethod
    def search_ids(cls, ids: list, index_name: str) -> list:
        """
        :param ids: a list of ids
        :param index_name:
        :return: return a list of object
        """
        body = {
            "from": 0, "size": len(ids),
            "query": {"ids": {"values": ids}}
        }
        return cls.ES_CONN.search(index=index_name, body=body)['hits']['hits']

    @classmethod
    def exist_ids(cls, ids: list, index_name: str) -> list:
        """
        which id in ids parameter is exist
        :param ids: a list of ids
        :param index_name:
        :return: return exist ids
        """
        results = cls.search_ids(ids, index_name)
        return [each['_id'] for each in results]

    @classmethod
    def create_multi_objs(cls, objs: list, index_name: str, timeout=10):
        """
        :param objs: a list of dictionaries that have below format
        {
            "id": "id",
            "data": {
                        "property1": value,
                        "property2": value,
                        ...
                    }
        }
        :param index_name:
        :param timeout
        :return:
        """
        body = [
            {
                '_index': index_name,
                '_id': each['id'],
                '_source': each['data'],
            }
            for each in objs
        ]
        result = helpers.bulk(cls.ES_CONN, body, raise_on_error=False, request_timeout=timeout)

    @classmethod
    def update_obj(cls, obj_id: str, index_name: str, obj: dict):
        """
        :param obj_id:
        :param index_name:
        :param obj:
        :return:
        """
        cls.ES_CONN.update(index=index_name, id=obj_id, body={'doc': obj})

    # methods for specific method

    @classmethod
    def get_expire_artists(cls, less_date: str, limit=20) -> list:
        """
        get the artist that have less last_check and return id of them
        :param less_date: less than which date
        :param limit: max number of results
        :return: a list of artist id
        """
        body = {
            "from": 0, "size": limit,
            "query": {
                "range": {
                    "last_check": {
                        "lte": less_date
                    }
                }
            }
        }
        results = cls.ES_CONN.search(index="artists", body=body)['hits']['hits']
        return [each['_id'] for each in results]

    @classmethod
    def get_unseen_songs(cls, limit=20) -> list:
        """
        get the songs with seen = false
        :param limit: max number of results
        :return: a list of song id
        """
        body = {
            "from": 0, "size": limit,
            "query": {
                "term": {
                    "effort": 0
                }
            }
        }
        results = cls.ES_CONN.search(index="songs", body=body)['hits']['hits']
        return [each['_id'] for each in results]

    @classmethod
    def get_no_feature_songs(cls, limit=20, max_search=5) -> list:
        """
        get the songs with fingerprint = "" and seen = True
        :param limit: max number of results
        :param max_search:
        :return: a list of song id
        """
        body = {
            "from": 0, "size": limit,
            "query": {
                "bool": {
                    "must": [
                        {
                            "range": {
                                "effort": {
                                    "lte": max_search,
                                    "gte": 1
                                }
                            }
                        },
                        {
                            "regexp": {
                                "fingerprint": ".{0}"
                            }
                        }
                    ]
                }
            }
        }
        results = cls.ES_CONN.search(index="songs", body=body)['hits']['hits']
        return [each['_id'] for each in results]

    @classmethod
    def increase_effort_song(cls, song_ids: list):
        """
        set effort += 1 for many ids
        :param song_ids:
        :return:
        """
        body = {
            "script": {
                "script": "ctx._source.effort += 1",
                "lang": "painless"
            },
            "query": {
                "ids": {
                    "values": song_ids
                }
            }
        }
        cls.ES_CONN.update_by_query(index="songs", body=body)

    @classmethod
    def update_song_list(cls, fingerprints: list, song_id: str):
        """
        update song list of fingerprint objs and add song_id to them
        :param fingerprints: a list of unique fingerprints
        :param song_id:
        :return:
        """

        body = {
            "script": {
                "inline": "ctx._source.songs.add(params.song_id)",
                "params": {
                    "song_id": song_id
                }
            },
            "query": {
                "ids": {
                    "values": fingerprints
                }
            }
        }
        cls.ES_CONN.update_by_query(index="fingerprints", body=body)

    @classmethod
    def score_songs(cls, song_ids: list, positions: dict) -> list:
        """
        search in songes based on positions and score them
        :param song_ids:
        :param positions:
        :return:
        """
        shoulds = [
            {
                "intervals": {
                    "message": {
                        "match": {
                            "query": fingerprint,
                            "filter": {
                                "script": {
                                    "source": "interval.start < {} ".format(positions[fingerprint])
                                }
                            }
                        }
                    }
                }
            }
            for fingerprint in positions
        ]

        body = {
            "size": len(song_ids),
            "_source": 'fingerprint',
            "query": {
                "bool": {
                    "must": {
                        "ids": {
                            "values": song_ids
                        }
                    },
                    "should": shoulds
                }
            }
        }
        results = cls.ES_CONN.search(index="songs", body=body)['hits']['hits']
        return results
