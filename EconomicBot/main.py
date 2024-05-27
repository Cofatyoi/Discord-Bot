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
    disnake.Activity(
        name="FiloqusCommunity",
        details="Coding"
    )
    try:
        print("Bot active")
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                        name TEXT,
                        id INTEGER,
                        cash INTEGER,
                        rep INTEGER,
                        lvl INTEGER,
                        ecclass TEXT,
                        job TEXT,
                        inventory TEXT,
                        ban TEXT,
                        mute TEXT,
                        kick TEXT
        )""")
        connection.commit()

        for guild in client.guilds:
            for member in guild.members:
                cursor.execute("SELECT id FROM users WHERE id = ?", (member.id,))
                if cursor.fetchone() is None:
                    print("База данных создаётся")
                    cursor.execute("INSERT INTO users(name, id, cash, rep, lvl, ecclass, job, inventory) VALUES (?, ?, 0, 0, 1, ?, ?, ?, ?)", (str(member), member.id, "Отсутствует", "Подработка", "Ничего", "Нету"))
                    connection.commit()
    except sqlite3.Error as e:
        print(f"QLS ошибка: {e}")
    finally:
        cursor.close()

client.run(settings['Token'])
