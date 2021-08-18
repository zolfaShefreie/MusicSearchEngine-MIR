import ast
import os


class CDict:

    def __init__(self, path):
        self.path = path
        self.__dict_struct = dict()
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            file = open(self.path, 'r')
            self.__dict_struct = ast.literal_eval(file.read())
            file.close()

    def _save(self):
        file = open(self.path, 'w')
        file.write(str(self.__dict_struct))
        file.close()

    def ___getitem__(self, key):
        return self.__dict_struct[key]

    def update(self, new_dict: dict):
        self.__dict_struct.update(new_dict)
        self._save()

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


if __name__ == '__main__':
    cdict = CDict("./l")
    cdict.update({"man": 90})
    cdict.update({"man1": 90})
    print(cdict.keys())
    for each in cdict:
        print(each)
