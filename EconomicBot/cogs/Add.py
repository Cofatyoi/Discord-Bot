import disnake
from disnake.ext import commands

class Add(commands.Cog):
    def __init__(self, bot: commands.Bot, conn):
        self.bot = bot
        self.conn = conn

    @commands.slash_command(
            name="add",
            description="Админ комманда для теста. Использовать только в том случае, если вы хотите выдать всё и сразу"
    )
    @commands.has_permissions(administrator=True)
    async def add(
        self, 
        inter, 
        member: disnake.Member, 
        classes: str = commands.Param(choices=['Senior', 'Middle', 'Junior']), 
        job: str = commands.Param(choices=['Программист', '3D Дизайнер', '2D Дизайнер', 'Строитель', 'Подработка', 'Косметолог', 'Столяр', 'Бухгалтер']), 
        money: int = commands.Param(description="Выдать деньги участнику сервера"), 
        rep: int = commands.Param(description="Выдать репутацию участнику сервера"), 
        lvl: int = commands.Param(choices=[1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100], description='Выдать уровень участнику сервера')
        ):
        cursor = self.conn.cursor()

    #Command
        if classes is not None:
            cursor.execute("UPDATE users SET ecclass = ?, job = ? WHERE id = ?", (classes, job, member.id))
            cursor.execute("UPDATE users SET cash = cash + ? WHERE id = ?", (money, member.id))
            cursor.execute("UPDATE users SET rep = rep + ? WHERE id = ?", (rep, member.id))
            cursor.execute("UPDATE users SET lvl = lvl + ? WHERE id = ?", (lvl, member.id))
            self.conn.commit()
            await inter.send(embed=disnake.Embed(
                title="Класс выдан успешно!",
                description=f"Участнику {member.global_name} был выдан класс {classes}, работа {job}. Так же было выдано {money} 🌕, {rep} репутации, {lvl} уровень",
                color=disnake.Colour.og_blurple()
            ))
        self.conn.commit()
        cursor.close()