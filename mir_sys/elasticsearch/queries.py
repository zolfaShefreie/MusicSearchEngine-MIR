from elasticsearch import Elasticsearch


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
