import disnake
from disnake.ext import commands
import sqlite3
from config import settings
from Cogs import load_cog

intents = disnake.Intents.all()
intents.messages = True  # Enable intent for message handling
client = commands.Bot(command_prefix=settings['Prefix'], intents=intents)
client.remove_command('help')

# Database connection
connection = sqlite3.connect('server.db')
load_cog(client, connection)

@client.event
async def on_ready():
    activity = disnake.Game(name="FiloqusCommunity")
    await client.change_presence(activity=activity)
    
    print("Bot active")
    
    try:
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                        name TEXT,
                        id INTEGER PRIMARY KEY,
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
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        
    finally:
        cursor.close()

client.run(settings['Token'])
