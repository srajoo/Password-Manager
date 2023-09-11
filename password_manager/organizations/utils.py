# utils.py

import uuid

def generate_unique_link():
    unique_link = str(uuid.uuid4())
    return unique_link