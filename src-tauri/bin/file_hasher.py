import hashlib
import re

class FileHash():
    '''
    The FileHash class takes in a file, and hashes it using SHA256 hash algorithm
    
    '''
    def hash(self, file):
        '''Hashes a file, and returns the SHA256 hash value'''
        BLOCK_SIZE = 65536
        file_hash = hashlib.sha256()
        with open(file, 'rb') as f: 
            fb = f.read(BLOCK_SIZE)
            while len(fb) > 0: 
                file_hash.update(fb) 
                fb = f.read(BLOCK_SIZE)

        return file_hash.hexdigest()

    def compare(self, hash_one, hash_two):
        '''
        compares two hashes
        hash_one and hash_two can either be a file path
        or a SHA256 hash
        returns True if a match
        
        '''
        try:
            hash_one = self.hash(hash_one)
        except:
            print(f'...{hash_one[-20:]} | NOT A FILE TYPE - COMPARING AS HASH')

        try:
            hash_two = self.hash(hash_two)
        except:
            print(f'...{hash_two[-20:]} | NOT A FILE TYPE - COMPARING AS HASH')

        if hash_one == hash_two:
            print('MATCH')
            return True
        else:
            print('FAILED MATCH')
            return False

if __name__ == '__main__':
    #test
    value = FileHash().compare('.\database\\20210419\ADJTIME.Dbf', '.\database\\20210420\ADJTIME.Dbf')
