import hashlib
import re

class FileHash():
    def __init__(self):
        pass

    def hash(self, file):
        BLOCK_SIZE = 65536
        file_hash = hashlib.sha256()
        with open(file, 'rb') as f: 
            fb = f.read(BLOCK_SIZE)
            while len(fb) > 0: 
                file_hash.update(fb) 
                fb = f.read(BLOCK_SIZE)

        return file_hash.hexdigest()

    def compare(self, hash_one, hash_two):

        try:
            hash_one = self.hash(hash_one)
        except:
            print(f'{hash_one} is not a file - assuming it is a hash')
        try:
            hash_two = self.hash(hash_two)
        except:
            print(f'{hash_two} is not a file - assuming it is a hash')

        print(hash_one, hash_two)

        if hash_one == hash_two:
            print('Hash Values Match')
            return True
        else:
            print('Hashes do not match')
            return False

if __name__ == '__main__':

    value = FileHash().compare("8a4751c078d26d89ab5a4fe8647e4fafe46d4bde06eec834fa5949d522d40b31", ".\database\\20210416\ADJTIME.Dbf")
    print(value)
