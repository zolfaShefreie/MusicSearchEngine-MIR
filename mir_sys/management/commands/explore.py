from django.core.management.base import BaseCommand
from multiprocessing import Pool

from mir_sys.indexer.index_management import management


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        management()
