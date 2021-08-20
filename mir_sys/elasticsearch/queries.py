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
        return cls.ES_CONN.search(index=index_name, body={"query": {"ids": {"values": ids}}})['hits']['hits']

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
    def create_multi_objs(cls, objs: list, index_name: str):
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
        result = helpers.bulk(cls.ES_CONN, body, raise_on_error=False)

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
