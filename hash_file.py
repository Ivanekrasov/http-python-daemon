import hashlib
from config import db, File


def hash_file(filename):
    file_content = filename.read()
    hashed_filename = hashlib.md5(file_content).hexdigest()
    db.session.add(File(filename=filename.filename, hash=hashed_filename))
    db.session.commit()
    return hashed_filename
