from elasticsearch import Elasticsearch, helpers


class Queries:
    ES_CONN = Elasticsearch()

    # methods for all indices

    @classmethod
    def search_ids(cls, ids: list, index_name: str, timeout=60) -> list:
        """
        :param ids: a list of ids
        :param index_name:
        :param timeout: 60
        :return: return a list of object
        """
        body = {
            "from": 0, "size": len(ids),
            "query": {"ids": {"values": ids}}
        }
        return cls.ES_CONN.search(index=index_name, body=body, request_timeout=timeout)['hits']['hits']

    @classmethod
    def exist_ids(cls, ids: list, index_name: str, timeout=60) -> list:
        """
        which id in ids parameter is exist
        :param ids: a list of ids
        :param index_name:
        :param timeout: 60
        :return: return exist ids
        """
        results = cls.search_ids(ids, index_name, timeout)
        return [each['_id'] for each in results]

    @classmethod
    def create_multi_objs(cls, objs: list, index_name: str, timeout=60):
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
    def update_obj(cls, obj_id: str, index_name: str, obj: dict, timeout=60):
        """
        :param obj_id:
        :param index_name:
        :param obj:
        :param timeout: 60
        :return:
        """
        cls.ES_CONN.update(index=index_name, id=obj_id, body={'doc': obj}, request_timeout=timeout)

    # methods for specific method

    @classmethod
    def get_expire_artists(cls, less_date: str, limit=20, timeout=60) -> list:
        """
        get the artist that have less last_check and return id of them
        :param less_date: less than which date
        :param limit: max number of results
        :param timeout:
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
        results = cls.ES_CONN.search(index="artists", body=body, request_timeout=timeout)['hits']['hits']
        return [each['_id'] for each in results]

    @classmethod
    def get_unseen_songs(cls, limit=20, timeout=60) -> list:
        """
        get the songs with seen = false
        :param limit: max number of results
        :param timeout: 60
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
        results = cls.ES_CONN.search(index="songs", body=body, request_timeout=timeout)['hits']['hits']
        return [each['_id'] for each in results]

    @classmethod
    def get_no_feature_songs(cls, limit=20, max_search=5, timeout=60) -> list:
        """
        get the songs with fingerprint = "" and seen = True
        :param limit: max number of results
        :param max_search:
        :param timeout: 60
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
                        }
                    ],
                    "must_not": [
                        {
                            "regexp": {
                                "fingerprint": ".{4}"
                            }
                        }
                    ]
                }
            }
        }
        results = cls.ES_CONN.search(index="songs", body=body, request_timeout=timeout)['hits']['hits']
        return [each['_id'] for each in results]

    @classmethod
    def increase_effort_song(cls, song_ids: list, timeout=60):
        """
        set effort += 1 for many ids
        :param song_ids:
        :param timeout: 60
        :return:
        """
        body = {
            "query": {
                "ids": {
                    "values": song_ids
                }
            },
            "script": {
                "source": "ctx._source.effort += 1",
                "lang": "painless"
            }
        }
        print(song_ids)
        cls.ES_CONN.update_by_query(index="songs", body=body, request_timeout=timeout)

    @classmethod
    def update_song_list(cls, fingerprints: list, song_id: str, timeout=60):
        """
        update song list of fingerprint objs and add song_id to them
        :param fingerprints: a list of unique fingerprints
        :param song_id:
        :param timeout: 60
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
        cls.ES_CONN.update_by_query(index="fingerprints", body=body, request_timeout=timeout)

    @classmethod
    def score_songs(cls, song_ids: list, positions: dict, timeout=60) -> list:
        """
        search in songes based on positions and score them
        :param song_ids:
        :param positions:
        :param timeout: 60
        :return:
        """
        shoulds = [
            {
                "intervals": {
                    "fingerprint": {
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
        results = cls.ES_CONN.search(index="songs", body=body, request_timeout=timeout)['hits']['hits']
        return results
