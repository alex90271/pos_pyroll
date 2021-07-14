import hashlib

file = ".\ADJTIME.Dbf"
BLOCK_SIZE = 65536

first_hash = '8a4751c078d26d89ab5a4fe8647e4fafe46d4bde06eec834fa5949d522d40b31'

file_hash = hashlib.sha256()
with open(file, 'rb') as f: 
    fb = f.read(BLOCK_SIZE)
    while len(fb) > 0: 
        file_hash.update(fb) 
        fb = f.read(BLOCK_SIZE)

updated_hash = file_hash.hexdigest()

if updated_hash == first_hash:
    print('same file')
else:
    print('The SHA256 Hash has changed')
    print(updated_hash)
