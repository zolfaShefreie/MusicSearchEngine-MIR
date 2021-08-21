from django.core.management.base import BaseCommand
from multiprocessing import Pool

from mir_sys.elasticsearch.queries import Queries
from mir_sys.utils.custom_base64 import NumBase64


class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def handle(self, *args, **kwargs):
        args = [(i*(2**12), (i+1)*(2**12)) for i in range((2**12))]
        pool = Pool(10)
        pool.starmap(self.run_block, args)
        pool.close()
        pool.terminate()

    @staticmethod
    def run_block(start: int, end: int):

        objs = list()
        for num in range(start, end):
            bin_num = bin(num).lstrip("0b").zfill(24)
            objs.append(
                {
                    'id': NumBase64.encode_binary_to_base64(bin_num),
                    'data': {
                        'songs': []
                    }
                }
            )
        Queries.create_multi_objs(objs, "fingerprints", 60)
