import disnake
from disnake.ext import commands

class Profile(commands.Cog):
    def __init__(self, bot: commands.Bot, conn):
        self.bot = bot
        self.conn = conn

    @commands.slash_command(
            name="profile",
            description="Открывает профиль игрока"
    )
    
    async def profile(self, inter, member: disnake.Member):
        
    #Cursor execute
        
        cursor = self.conn.cursor()
        profile_data = cursor.execute("SELECT cash, rep, lvl, ecclass, job FROM users WHERE id = ?", (member.id,))
        profile_data = cursor.fetchone()

    #SQLite ERROR
        
        if profile_data is None:
            cursor.execute("INSERT INTO users(name, id, cash, rep, lvl, ecclass, job, inventory) VALUES (?, ?, 0, 0, 1, ?, ?, ?)", (str(member), member.id, "Отсутствует", "Подработка", "Ничего"))
            profile_data = (0, 0, 1, "Отсутствует", "Подработка")
            
    #Command
            
        await inter.send(
            embed=disnake.Embed(
                title=f"Профиль пользователя **{member.global_name}**",
                description=(
                    " ``Базовая информация`` \n"
                    f"``` Баланс: {profile_data[0]} ```"
                    f"``` Уровень: {profile_data[2]} ```"
                    f"``` Репутация: {profile_data[1]} ```"
                    f"``` Класс: {profile_data[3]} ```"
                    f"``` Работа: {profile_data[4]} ```"),
                    color=disnake.Colour.og_blurple()),
                    )
        cursor.close()