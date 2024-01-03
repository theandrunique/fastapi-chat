import uuid


def generate_chat_id():
    return str(uuid.uuid4())


def del_id(d: dict):
    d.pop("_id")
    return d
