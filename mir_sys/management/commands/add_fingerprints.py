from django.core.management.base import BaseCommand
import itertools

from mir_sys.elasticsearch.queries import Queries
from mir_sys.utils.custom_base64 import NumBase64


def get_all_rel_fingerprints(num_binary: str, max_hamming_distance=2):
    rel_fingerprints = set()

    for i in range(max_hamming_distance):
        for each in itertools.combinations(range(len(num_binary)), i):
            new = str().join([str(0**int(num_binary[i])) if i in each else num_binary[i]
                              for i in range(len(num_binary))])
            rel_fingerprints.add(new)
    return list(rel_fingerprints)


class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def handle(self, *args, **kwargs):
        for i in range((2**12)-1):
            objs = list()
            for num in range((2**10)*i, (2**10)*(i+1)):
                bin_num = bin(num).rstrip("0b").zfill(24)
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
            Queries.create_multi_objs(objs, "fingerprints")
            print('done', i)
