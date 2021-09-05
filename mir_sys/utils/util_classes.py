import ast
import os
import itertools

from mir_sys.utils.custom_base64 import NumBase64


def hamming_distance(u: iter, v: iter) -> float:
    """
    calculate the hamming distance
        diffs/len
    :param u: iter obj
    :param v: iter obj
    :return: hamming distance
    """
    score = 0
    for i in range(len(u)):
        if u[i] != v[i]:
            score += 1
    return score/len(u)


class CDict:
    MAX_CHANGES = 20000

    def __init__(self, path):
        self.path = path
        self.__change_num = 0
        self.__dict_struct = dict()
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            file = open(self.path, 'r', encoding="utf-8")
            self.__dict_struct = ast.literal_eval(file.read())
            file.close()

    def save(self):
        file = open(self.path, 'w', encoding="utf-8")
        file.write(str(self.__dict_struct))
        file.close()
        print("saved")

    def __getitem__(self, key):
        return self.__dict_struct[key]

    def update(self, new_dict: dict):
        self.__dict_struct.update(new_dict)
        self.__change_num += 1
        if self.__change_num >= self.MAX_CHANGES:
            self.__change_num = 0
            self.save()

    def __iter__(self):
        self.count = 0
        return self

    def __next__(self):
        if self.count >= len(self.__dict_struct):
            raise StopIteration
        else:
            self.count += 1
            return list(self.__dict_struct.keys())[self.count - 1]

    def __len__(self):
        return len(self.__dict_struct)

    def keys(self):
        return self.__dict_struct.keys()

    def items(self):
        return self.__dict_struct.items()

    def values(self):
        return self.__dict_struct.values()


class FingerprintSim:
    MAX_BIT = 24
    CHANGE_INDEX_LIST = [x for x in itertools.combinations(range(24), 1)]

    @classmethod
    def create_rel_fingerprints(cls, fingerprint: str) -> list:
        """
        create rel_fingerprints with maximum 1 hamming_distance for a fingerprint
        :param fingerprint:
        :return: a list of rel_fingerprints
        """
        rel_fingerprints = set()
        binary_fingerprint = NumBase64.decode_to_binary(fingerprint)
        for index in cls.CHANGE_INDEX_LIST:
            new = "".join([str(0 ** int(binary_fingerprint[i])) if i in index else binary_fingerprint[i]
                           for i in range(len(binary_fingerprint))])

            rel_fingerprints.add(NumBase64.encode_binary_to_base64(new))
        return list(rel_fingerprints) + [fingerprint]

    @classmethod
    def create_file(cls, path="./synonyms.txt"):
        """
        this function create synonyms file like elastic synonyms style
        :param path: path of the file that will be saved
        :return:
        """
        file = open(path, 'a')
        file_content = str()
        conditions = [(2 ** 14) * i for i in range((2 ** 10) + 1)]
        for num in range(2 ** cls.MAX_BIT):
            bin_num = bin(num).lstrip("0b").zfill(cls.MAX_BIT)
            encode_num = NumBase64.encode_binary_to_base64(bin_num)
            file_content += f"{encode_num}=>"
            rels = ",".join(cls.create_rel_fingerprints(encode_num)).rstrip(",")
            file_content += f"{rels}\n"
            if num in conditions:
                file.write(file_content)
                file_content = str()

        if file_content:
            file.write(file_content)
            file_content = str()
        file.close()


if __name__ == '__main__':
    cdict = CDict("./l")
    cdict.update({"man": 90})
    cdict.update({"man1": 90})
    print(cdict.keys())
    for each in cdict:
        print(each)
