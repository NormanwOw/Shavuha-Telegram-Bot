import json
import random
import string
import hashlib

TIME_ZONE = 5


def set_json(path: str, users: dict):
    with open(path, 'w') as file:
        json.dump(users, file, ensure_ascii=False)


def get_json(path: str) -> dict:
    with open(path, 'r') as file:
        return json.load(file)


def gen_password() -> str:
    password = ''
    pw_str = string.digits+string.ascii_uppercase
    for ch in ['I', 'O', '0', 'J', 'Z', 'C']:
        pw_str = pw_str.replace(ch, '')
    length = len(pw_str)
    for i in range(5):
        password += pw_str[random.randint(0, length-1)]
    return password


def update_password() -> str:
    pw = gen_password()
    pw_dict = {'staff': pw}
    set_json('data.json', pw_dict)
    return pw


def generate_id() -> str:
    hash_data = ''
    for i in range(10):
        hash_data += string.ascii_letters[random.randint(0, len(string.ascii_letters)-1)]

    return hashlib.md5(hash_data.encode()).hexdigest()
