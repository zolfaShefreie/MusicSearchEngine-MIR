from elasticsearch import Elasticsearch
from django.core.management.base import BaseCommand
from django.conf import settings

from mir_sys.elasticsearch.index_schemas import SCHEMA


class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        el = Elasticsearch()
        for each in SCHEMA:
            el.delete_by_query(index=each['index_name'], body={"query": {"match_all": {}}})