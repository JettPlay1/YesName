import asyncio
import logging

from db import engine
from db.classes import *
from sqlalchemy import select, insert, update, desc


async def get_user_data(user_id: int) -> dict:
    try:
        async with engine.connect() as conn:
            result = await conn.execute(select(User).where(User.id == user_id))
            row = result.fetchone()
            if len(row) == 0:
                return
            user_data = {}
            user_data["user_id"]         = row[0]
            user_data["name"]            = row[1]
            user_data["surname"]         = row[2]
            user_data["score"]           = row[3]
            user_data["task_id"]         = row[4]
            user_data["completed_tasks"] = row[5]

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
            
            result = await conn.execute(select(User).order_by(desc(User.score)))
            users = []
            for row in result.fetchall():
                user_data = {}
                user_data["id"]              = row[0]
                user_data["name"]            = row[1]
                user_data["surname"]         = row[2]
                user_data["score"]           = row[3]
                user_data["task_id"]         = row[4]
                user_data["completed_tasks"] = row[5]
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


async def get_task_data(task_id: int) -> dict:
    try:
        async with engine.connect() as conn:
            result = await conn.execute(select(Task).where(Task.id == task_id))
            row = result.fetchone()
            task_data = {}
            task_data["id"]          = row[0]
            task_data["name"]        = row[1]
            task_data["description"] = row[2]
            task_data["score"]       = row[3]
            task_data["flag"]        = row[4]
            task_data["final_flag"]  = row[5]

            return task_data
        
    except Exception as e:
        logging.error(f"Произошла ошибка при запросе к БД (task_data): {e}")
        return {}


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
