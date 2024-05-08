import disnake
from disnake.ext import commands


class SendAMoney(commands.Cog):
    def __init__(self, bot: commands.Bot, conn):
        self.bot = bot
        self.conn = conn

    @commands.slash_command(
        name="send",
        description="Открывает профиль игрока"
    )
    async def profile(self, inter, member: disnake.Member, amount: commands.Range[int, 0, 10000] = commands.Param(
        description="Выберите сумму которую хотите отправить")):
        user_id = inter.user

        # Cursor execute

        cursor = self.conn.cursor()
        member_data = cursor.execute("SELECT cash, rep, lvl, ecclass, job FROM users WHERE id = ?",
                                     (member.id,))  # mention member\
        member_data = cursor.fetchone()
        user_data = cursor.execute("SELECT cash, rep, lvl, ecclass, job FROM users WHERE id = ?",
                                   (user_id.id,))  # user its member who use the command
        user_data = cursor.fetchone()

        # SQLite ERROR

        if member_data is None:
            cursor.execute(
                "INSERT INTO users(name, id, cash, rep, lvl, ecclass, job, inventory) VALUES (?, ?, 0, 0, 1, ?, ?, ?)",
                (str(member), member.id, "Отсутствует", "Подработка", "Ничего"))
            member_data = (0, 0, 1, "Отсутствует", "Подработка")

        # Errors

        if user_id.id == member.id:  # If user send money for himself
            await inter.send(embed=disnake.Embed(
                title="Проблема в использовании комманды **send**",
                description=f"Вы не можете выбрать себя что бы отправить деньги",
                color=disnake.Colour.og_blurple()
            ))
            return
        if user_data[0] < amount:  # If user write a amount > himself cash
            await inter.send(embed=disnake.Embed(
                title="Проблема в использовании комманды **send**",
                description=f"Вы не можете отправлять такую сумму денег ибо она привышает ваш баланс",
                color=disnake.Colour.og_blurple()
            ))
            return

        # Command

        cursor.execute("UPDATE users SET cash = cash + ? WHERE id = ?", (amount, member.id))
        cursor.execute("UPDATE users SET cash = cash - ? WHERE id = ?", (amount, user_id.id))
        self.conn.commit()
        await inter.send(embed=disnake.Embed(
            title="Деньги отправлены успешно!",
            description=f"Вы отправили {member.global_name} сумму в {amount} 🌕",
            color=disnake.Colour.og_blurple()
        ))
        cursor.close()
