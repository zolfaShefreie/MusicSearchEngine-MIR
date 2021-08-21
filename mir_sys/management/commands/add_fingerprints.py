from django.core.management.base import BaseCommand
from multiprocessing import Pool
import itertools

from mir_sys.elasticsearch.queries import Queries
from mir_sys.utils.custom_base64 import NumBase64


def get_all_rel_fingerprints(num_binary: str, max_hamming_distance=2):
    rel_fingerprints = set()

    for i in range(1, max_hamming_distance+1):
        for each in itertools.combinations(range(len(num_binary)), i):
            new = str().join([str(0**int(num_binary[i])) if i in each else num_binary[i]
                              for i in range(len(num_binary))])
            rel_fingerprints.add(new)
    return list(rel_fingerprints)


class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def handle(self, *args, **kwargs):
        args = [(i*(2**12), (i+1)*(2**12)) for i in range((2**12)-1)]
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
                        'rel_fingerprint': [NumBase64.encode_binary_to_base64(each)
                                            for each in get_all_rel_fingerprints(bin_num)],
                        'songs': []
                    }
                }
            )
        Queries.create_multi_objs(objs, "fingerprints", 60)

