import disnake
from disnake.ext import commands
import random as r

class Job(commands.Cog):
    def __init__(self, bot: commands.Bot, conn):
        self.bot = bot
        self.conn = conn

    @commands.slash_command(
            name="job",
            description="при использовании исполняет вашу работу. Работает раз в 8 часов"
    )

    @commands.cooldown(1, (28800), commands.BucketType.user)
    async def job(
        self,
        inter,
        job: str = commands.Param(description='Выберите работу на которой будете работать.', choices=['Программист', '3D Дизайнер', '2D Дизайнер', 'Строитель', 'Подработка', 'Косметолог', 'Столяр', 'Бухгалтер'])
        ):
        user_id = inter.user
        
    #Cursor execute
        
        cursor = self.conn.cursor()
        profile_data = cursor.execute("SELECT cash, rep, lvl, ecclass, job FROM users WHERE id = ?", (user_id.id,))
        profile_data = cursor.fetchone()

    #SQLite ERROR
        
        if profile_data is None:
            cursor.execute("INSERT INTO users(name, id, cash, rep, lvl, ecclass, job) VALUES (?, ?, 0, 0, 1, ?, ?)", (str(user_id), user_id.id, "Отсутствует", "Подработка"))
            profile_data = (0, 0, 1, "Отсутствует", "Подработка")

    #ERROR
            
        if job != profile_data[4]:
            await inter.send(embed=disnake.Embed(
                title="Проблема в использовании комманды **job**",
                description=f"Вы не можете выбрать работу которой нету у вас в профиле! Если у вас отсутствует работа тогда выберите 'Подработка'",
                color=disnake.Colour.og_blurple()
            ))
            
        
    #Command
        jobs = profile_data[4]
        classes = profile_data[3]
        for i, min, max in [["3D Дизайнер", 500, 1500], ["Программист", 1000, 3000], ["2D Дизайнер", 750, 2000], ["Строитель", 1000, 2500], ["Подработка", 500, 1000], ["Косметолог", 750, 2000], ["Столяр", 1250, 2750], ["Бухгалтер", 750, 2000]]:
            if job == i and job == jobs:
                amount = r.randint(min, max)
                if job == 'Программист' and classes == "Senior":
                    amount = amount * 3
                elif classes == "Middle":
                    amount = amount * 2
                elif classes == "Junior":
                    amount = amount * 1.5
                amount_rep = r.randint(1, 10)
                cursor.execute("UPDATE users SET cash = cash + ?, rep = rep + ? WHERE id = ?", (amount, amount_rep, user_id.id))
                self.conn.commit()
                await inter.send(embed=disnake.Embed(
                    title="Вы успешно поработали!",
                    description=f"Спасибо что поработали в сфере {job}! За эти 8 часов работы вы получили {amount} 🌕. Так же вы получили {amount_rep} репутации. Вам нужно отдохнуть поэтому у вас кулдаун на комманду 8 часов",
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