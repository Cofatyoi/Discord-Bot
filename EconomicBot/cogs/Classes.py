import disnake
from disnake.ext import commands

class Classes(commands.Cog):
    def __init__(self, bot: commands.Bot, conn):
        self.bot = bot
        self.conn = conn

    @commands.slash_command(
            name="classes",
            description="Senior: 25k🌕, Middle: 15k🌕, Junior: 10k🌕"
    )
    async def classes(
        self,
        inter, 
        classes: str = commands.Param(description="Выберите класс для покупки.", choices=["Senior", "Middle", "Junior"])):
        user_id = inter.user

    #Cursor execute

        cursor = self.conn.cursor()
        profile_data = cursor.execute("SELECT cash, rep, lvl, ecclass, job FROM users WHERE id = ?", (user_id.id,))
        profile_data = cursor.fetchone()

    #SQLite ERROR
        
        if profile_data is None:
            cursor.execute("INSERT INTO users(name, id, cash, rep, lvl, ecclass, job) VALUES (?, ?, 0, 0, 1, ?, ?)", (str(user_id), user_id.id, "Отсутствует", "Подработка"))
            profile_data = (0, 0, 1, "Отсутствует", "Подработка")

    #ERRORS + COMMAND
        for ecclass, cost, mult in [["Senior", 25000, 3], ["Middle", 15000, 2], ["Junior", 7500, 1.5]]:
            if classes == ecclass:  # Если класс совпадает с текущим классом из списка
                if profile_data[0] >= cost:  # Если у пользователя достаточно лун для покупки класса
                    cursor.execute("UPDATE users SET ecclass = ? WHERE id = ?", (classes, user_id.id))
                    cursor.execute("UPDATE users SET cash = cash - ? WHERE id = ?", (cost, user_id.id))
                    self.conn.commit()
                    await inter.send(embed=disnake.Embed(
                        title=f"Вы успешно купили класс {classes}!",
                        description=f"Теперь у вас есть x{mult} лун для работы 'Программист, 3D Дизайнер, 2D Дизайнер'",
                        color=disnake.Colour.og_blurple()
                    ))
                    cursor.close()
                else:
                    await inter.send(embed=disnake.Embed(
                        title="Проблема в использовании команды **classes**",
                        description=f"У вас недостаточно лун для покупки класса {classes}",
                        color=disnake.Colour.og_blurple()
                    ))
                return