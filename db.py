import json
from cfg import db_link

file_name = db_link


async def create_new_user(_id):
    _id = str(_id)
    data: dict
    with open(file_name, 'r') as f:
        data = json.load(f)
        if _id in data:
            return
        data[_id] = {}
        data[_id]["in_progress"] = []
        data[_id]["ready"] = []
    with open(file_name, 'w') as f:
        json.dump(data, f)


async def add_item(_id: int, task: str):
    """
    Добавляет task пользователю _id
    :param _id: id пользователя
    :param task: задача для добавления пользователю
    :return: статус задачи: 0 - ошибка, иначе None
    """
    _id = str(_id)
    status: str
    data: dict
    with open(file_name, 'r') as f:
        data = json.load(f)
        print(data)
        if _id not in data:
            return 0
    data[_id]["in_progress"].append(task)
    with open(file_name, 'w') as f:
        json.dump(data, f)


async def get_in_progress(_id: int):
    _id = str(_id)
    with open(file_name, 'r') as f:
        data = json.load(f)
        if _id in data:
            return data[_id]["in_progress"]
        else:
            return 0


async def get_ready(_id: int):
    _id = str(_id)
    with open(file_name, 'r') as f:
        data = json.load(f)
        if _id in data:
            return data[_id]["ready"]
        else:
            return 0


async def delete(_id: int, n: int):
    _id = str(_id)
    data: dict
    with open(file_name, 'r') as f:
        data = json.load(f)
        if _id not in data:
            return 0
    data[_id]["in_progress"].pop(n-1)
    with open(file_name, 'w') as f:
        json.dump(data, f)


async def to_ready(_id: int, n: int):
    _id = str(_id)
    data: dict
    with open(file_name, 'r') as f:
        data = json.load(f)
        if _id not in data:
            return 0
    print(data[_id]["in_progress"][n-1])
    data[_id]["ready"].append(data[_id]["in_progress"][n-1])
    data[_id]["in_progress"].pop(n-1)
    with open(file_name, 'w') as f:
        json.dump(data, f)