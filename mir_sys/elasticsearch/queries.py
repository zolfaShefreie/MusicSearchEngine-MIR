from elasticsearch import Elasticsearch, helpers


class Queries:
    ES_CONN = Elasticsearch()

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
