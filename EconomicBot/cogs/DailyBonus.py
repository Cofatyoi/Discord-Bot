import disnake
from disnake.ext import commands
import random as r

class DailyBonus(commands.Cog):
    def __init__(self, bot: commands.Bot, conn):
        self.bot = bot
        self.conn = conn

    @commands.slash_command(
            name="dailybonus",
            description="Ежедневный бонус"
    )

    @commands.cooldown(1, (86400), commands.BucketType.user)
    async def DailyBonus(self, inter):
        user_id = inter.user
        amount = r.randint(100, 1000)

    #Cursor execute
        
        cursor = self.conn.cursor()
        profile_data = cursor.execute("SELECT cash, rep, lvl, ecclass, job, inventory FROM users WHERE id = ?", (user_id.id,))
        profile_data = cursor.fetchone()

    #SQLite ERROR
        
        if profile_data is None:
            cursor.execute("INSERT INTO users(name, id, cash, rep, lvl, ecclass, job, inventory) VALUES (?, ?, 0, 0, 1, ?, ?, ?)", (str(user_id), user_id.id, "Отсутствует", "Подработка", "Ничего"))
            profile_data = (0, 0, 1, "Отсутствует", "Подработка")

    #Command
            
        cursor.execute("UPDATE users SET cash = cash + ? WHERE id = ?", (amount, user_id.id))
        self.conn.commit()
        await inter.send(embed=disnake.Embed(
            title="Ежедневный бонус выдан!",
            description=f"Спасибо что использовали ежедневную комманду {user_id.global_name}! Вы получили {amount} 🌕.",
            color=disnake.Colour.og_blurple()
        ))
        cursor.close()

    #Cooldown ERROR
        
    @commands.Cog.listener()
    async def on_slash_command_error(self, inter, error):
        if isinstance(error, commands.CommandOnCooldown):
            seconds = error.retry_after
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            
            await inter.response.send_message(embed=disnake.Embed( 
                title='Команда на задержке.', 
                description=f'Следующее использование команды будет доступно через `{int(hours)} часов, {int(minutes)} минут, {int(seconds)} секунд`', 
                colour=disnake.Colour.og_blurple()
            ))