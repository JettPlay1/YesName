import aiosqlite
import logging
import aiofiles


async def get_flag_part(user_id, flag):
    task_id = await get_user_task_id(user_id)
    users = await get_users_on_task(task_id)
    users = [a[0] for a in users]
    ind = users.index(user_id)
    parts_len = len(flag) // len(users)
    parts = []
    for i in range(len(users)-1):
        parts.append((i+1, flag[i:i+parts_len]))
    parts.append((len(users), flag[parts_len*(len(users)-1):]))

    return parts[ind]


async def get_users_on_task(task_id):
    try:
        async with aiosqlite.connect("./db/db.sql") as conn:
            cursor = await conn.execute(f"SELECT id FROM User_tb WHERE current_id_task={task_id}")
            users = await cursor.fetchall()
            return users
    except:
        return []


async def get_user_task_id(user_id):
    try:
        async with aiosqlite.connect("./db/db.sql") as conn:
            cursor = await conn.execute(f"SELECT current_id_task FROM User_tb WHERE id={user_id}")
            task_id = await cursor.fetchone()
            return task_id[0]
    except Exception as e:
        logging.error(f"{e}")
        return -1


async def get_flag(user_id):
    task_id = await get_user_task_id(user_id)
    flag = await get_flag_by_task_id(task_id)
    return flag


async def get_real_flag(user_id):
    task_id = await get_user_task_id(user_id)
    flag = await get_real_flag_by_task_id(task_id)
    return flag


async def get_real_flag_by_task_id(task_id):
    try:
        async with aiosqlite.connect("./db/db.sql") as conn:
            cursor = await conn.execute(f"SELECT real_flag FROM Task_tb WHERE id={task_id}")
            real_flag = await cursor.fetchone()
            return real_flag[0]
    except:
        return -1


async def get_flag_by_task_id(task_id):
    try:
        async with aiosqlite.connect("./db/db.sql") as conn:
            cursor = await conn.execute(f"SELECT flag FROM Task_tb WHERE id={task_id}")
            flag = await cursor.fetchone()
            return flag[0]
    except:
        return -1


async def show_tasks():
    async with aiosqlite.connect("./db/db.sql") as conn:
        cursor = await conn.execute("SELECT * FROM User_tb")
        users = await cursor.fetchall()
    print(users)


async def get_task(user_id) -> str:
    try:
        async with aiosqlite.connect("./db/db.sql") as conn:
            cursor = await conn.execute(f"SELECT current_id_task FROM User_tb WHERE id={user_id}")
            task_id = await cursor.fetchone()
            task_id = task_id[0]
            if task_id == -1:
                return "У вас нет активного задания."
            cursor = await conn.execute(f"SELECT Name FROM Task_tb WHERE id={task_id}")
            task_name = await cursor.fetchone()
            return task_name[0]
    except Exception as e:
        logging.error(f"{e}")
        return "Произошла ошибка при обработке"


async def add_user(user_id) -> bool:
    users_list = await get_users_list()
    length = len(users_list)
    async with aiofiles.open("./db/scam.txt", "r") as file:
        tasks = await file.readlines()
        tasks = tasks[length].strip().split(':')[1].split(',')

    try:
        async with aiosqlite.connect("./db/db.sql") as conn:
            await conn.execute(f"INSERT INTO User_tb (id,name,surename,score,current_id_task,completed_tasks,team)\
                                 VALUES ({user_id},'Вася','Пупкин',0,{tasks[0]},'','Домино')")
            await conn.commit()
        
        return True
    
    except Exception as e:
        logging.error(f"{e}")
        return False



async def get_task_list() -> list:
    try:
        async with aiosqlite.connect("./db/db.sql") as conn:
            cursor = await conn.execute("SELECT id FROM Task_tb")
            tasks = await cursor.fetchall()

            return tasks
    except Exception as e:
        logging.error(f"Произошла ошибка при получении списка заданий: {e}")
        return []


async def get_users_list() -> list:
    try:
        async with aiosqlite.connect("./db/db.sql") as conn:
            cursor = await conn.execute("SELECT id FROM User_tb")
            users = await cursor.fetchall()
            return users
    except Exception as e:
        logging.error(f"Произошла ошибка при получении списка пользователей: {e}")
        return []


async def set_tasks(user_tasks: dict) -> bool:
    try:
        async with aiosqlite.connect("./db/db.sql") as conn:
            for user_id, tasks in user_tasks.items():
                await conn.execute(f"UPDATE User_tb SET tasks={';'.join(tasks)} WHERE id={user_id};")
                await conn.commit()
        return True
    except Exception as e:
        logging.error(f"Произошла ошибка при добавлении заданий в БД: {e}")
        return False