import asyncio
import logging
import random
from math import ceil

from db import engine
from db.classes import *
from sqlalchemy import select, insert, update, desc


async def get_user_data(user_id: int) -> dict:
    try:
        async with engine.connect() as conn:
            result = await conn.execute(select(User).where(User.id == user_id))
            row = result.fetchone()
            if row is None:
                return
            user_data = {}
            user_data["user_id"]         = row[0]
            user_data["name"]            = row[1]
            user_data["surname"]         = row[2]
            user_data["score"]           = row[3]
            user_data["task_id"]         = row[4]
            user_data["subtask_id"]      = row[5]
            user_data["completed_tasks"] = row[6]

            return user_data
        
    except Exception as e:
        logging.error(f"Произошла ошибка при запросе к БД (user_data): {e}")
        return
    

# Column - Класс, реализующий таблицу, и столбец данного класса. Н-р: User.id
# По умолчанию возвращает список пользователей отсортированных по количеству очков
async def get_all_users(column: any = None, 
                        value: any = None) -> list[dict]:
    try:
        async with engine.connect() as conn:
            if column and value:
                result = await conn.execute(select(User).where(column == value))
            else:
                result = await conn.execute(select(User).order_by(desc(User.score)))
            users = []
            for row in result.fetchall():
                user_data = {}
                user_data["id"]              = row[0]
                user_data["name"]            = row[1]
                user_data["surname"]         = row[2]
                user_data["score"]           = row[3]
                user_data["task_id"]         = row[4]
                user_data["subtask_id"]      = row[5]
                user_data["completed_tasks"] = row[6]
                users.append(user_data)

            return users
        
    except Exception as e:
        logging.error(f"Произошла ошибка при запросе к БД (users): {e}")
        return []


async def insert_user(user_id: int, 
                      name: str = "default_name", 
                      surname: str = "default_name", 
                      score: int = 0, 
                      task_id: int = -1, 
                      completed_tasks: str = ""):
    try:
        async with engine.connect() as conn:
            await conn.execute(insert(User).values(id=user_id, 
                                                   name=name, 
                                                   surname=surname, 
                                                   score=score,
                                                   task_id=task_id, 
                                                   completed_tasks=completed_tasks
                                                   ))
            await conn.commit()
    except Exception as e:
        logging.error(f"Произошла ошибка при добавлении пользователя в БД: {e}")


async def update_user_by_id(user_id: int, 
                            column: any, 
                            value: any):
    try:
        async with engine.connect() as conn:
            await conn.execute(update(User).where(User.id == user_id).values({column: value}))
            await conn.commit()
    except Exception as e:
        logging.error(f"Произошла ошибка при добавлении пользователя в БД: {e}")


async def get_subtask_data(task_id: int) -> dict:
    try:
        async with engine.connect() as conn:
            result = await conn.execute(select(Subtask).where(Subtask.id == task_id))
            row = result.fetchone()
            task_data = {}
            task_data["id"]          = row[0]
            task_data["name"]        = row[1]
            task_data["description"] = row[2]
            task_data["task_id"]     = row[3]
            task_data["flag"]        = row[4]

            return task_data
        
    except Exception as e:
        logging.error(f"Произошла ошибка при запросе к БД (task_data): {e}")
        return {}


async def get_all_subtasks() -> dict:
    try:
        async with engine.connect() as conn:
            result = await conn.execute(select(Subtask))
            subtasks = []
            for row in result.fetchall():
                subtasks_data = {}
                subtasks_data["id"]          = row[0]
                subtasks_data["name"]        = row[1]
                subtasks_data["description"] = row[2]
                subtasks_data["task_id"]     = row[3]
                subtasks_data["flag"]        = row[4]
                subtasks.append(subtasks_data)

            return subtasks
        
    except Exception as e:
        logging.error(f"Произошла ошибка при запросе к БД (subtasks): {e}")
        return []


async def get_task_data(task_id: int) -> dict:
    try:
        async with engine.connect() as conn:
            result = await conn.execute(select(Task).where(Task.id == task_id))
            row = result.fetchone()
            task_data = {}
            task_data["id"]    = row[0]
            task_data["theme"] = row[1]
            task_data["score"] = row[2]
            task_data["flag"]  = row[3]

            return task_data
        
    except Exception as e:
        logging.error(f"Произошла ошибка при запросе к БД (task_data): {e}")
        return {}


async def get_all_tasks() -> dict:
    try:
        async with engine.connect() as conn:
            result = await conn.execute(select(Task))
            tasks = []
            for row in result.fetchall():
                task_data = {}
                task_data["id"]    = row[0]
                task_data["theme"] = row[1]
                task_data["score"] = row[2]
                task_data["flag"]  = row[3]
                tasks.append(task_data)

            return tasks
        
    except Exception as e:
        logging.error(f"Произошла ошибка при запросе к БД (tasks): {e}")
        return []


async def get_random_task(user_id):
    users = await get_all_users()
    users_count = len(users)
    tasks = await get_all_tasks()
    tasks_count = len(tasks)
    team_size = ceil(users_count / tasks_count)
    sizes = {}

    for task in tasks:
        sizes[task['id']] = 0

    for user in users:
        if user['task_id'] == -1:
            continue
        if sizes.get(user['task_id']):
            sizes[user['task_id']] += 1
            continue
        sizes[user['task_id']] = 1
    
    rem = []
    for key in sizes.keys():
        if sizes[key] >= team_size:
            rem.append(key)
    for r in rem: del sizes[r]

    task_id = random.choice(list(sizes.keys()))

    await update_user_by_id(user_id, User.task_id, task_id)

    subtasks = await get_all_subtasks()
    subtasks_count = len(subtasks)
    for i, user in enumerate(users):
        if user['id'] == user_id:
            subtask_id = subtasks[i % subtasks_count]['id']
            break
    
    await update_user_by_id(user_id, User.subtask_id, subtask_id)


async def get_flag_part(user_id, flag):
    user_data = await get_user_data(user_id)
    users = await get_all_users(User.task_id, user_data['task_id'])
    users = [user['id'] for user in users]
    ind = users.index(user_id)
    parts_len = len(flag) // len(users)
    parts = []
    for i in range(len(users)-1):
        parts.append((i+1, flag[i:i+parts_len]))
    parts.append((len(users), flag[parts_len*(len(users)-1):]))

    return parts[ind]
