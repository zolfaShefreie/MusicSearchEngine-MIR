from elasticsearch import Elasticsearch
from django.core.management.base import BaseCommand
from django.conf import settings

from mir_sys.elasticsearch.index_schemas import SCHEMA


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        el = Elasticsearch()
        for each in SCHEMA:
            el.indices.create(index=each['index_name'], body=each['schema'], ignore=[400, 404], request_timeout=7200)
        print(f"indices: {el.indices.get_alias('*')}")
