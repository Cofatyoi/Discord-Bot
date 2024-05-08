import disnake
from disnake.ext import commands
import sqlite3
from config import settings
from Cogs import load_cog

intents = disnake.Intents.default()
intents.messages = True  # Включаем интент для работы с сообщениями
client = commands.Bot(command_prefix=settings['Prefix'], intents=intents)
client.remove_command('help')


connection = sqlite3.connect('server.db')
load_cog(client, connection)

@client.event
async def on_ready():
    try:
        print("Бот готов к работе")
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                        name TEXT,
                        id INTEGER,
                        cash INTEGER,
                        rep INTEGER,
                        lvl INTEGER,
                        ecclass TEXT,
                        job TEXT,
                        inventory TEXT
        )""")
        connection.commit()

        for guild in client.guilds:
            for member in guild.members:
                cursor.execute("SELECT id FROM users WHERE id = ?", (member.id,))
                if cursor.fetchone() is None:
                    print("Дата база создаётся")
                    cursor.execute("INSERT INTO users(name, id, cash, rep, lvl, ecclass, job, inventory) VALUES (?, ?, 0, 0, 1, ?, ?, ?)", (str(member), member.id, "Отсутствует", "Подработка", "Ничего"))
                    connection.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()

@client.event
async def on_member_join(member):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM users WHERE id = ?", (member.id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO users VALUES (?, ?, 0, 0, 1, ?, ?, ?)", (str(member), member.id, "Отсутствует", "Подработка", "Ничего"))
            connection.commit()  # Commit after adding the user
            await member.send("Добро пожаловать на сервер! Ваш баланс установлен в 0.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()

client.run(settings['Token'])
