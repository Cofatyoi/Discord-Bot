import disnake
from disnake.ext import commands
import logging
import datetime
from Data_processing import ModerateProcessing, SQLProcessing

logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="a", encoding='utf-8', format="%(asctime)s %(levelname)s %(message)s")

class ModerateCommands(commands.Cog):
    def __init__(self, bot: commands.Bot, conn):
        self.bot = bot
        self.conn = conn
    
    @commands.slash_command(name="clear", description="Админ комманда. Очищает сообщения")
    async def clear(self, inter, amount: commands.Range[int, 0, 10000] = commands.Param(description="Выберите сколько сообщений хотите удалить")):
        try:
            ModerateProcessing.Check_permissions()

            deleted = await inter.channel.purge(limit=amount)
            logging.info(f"Очищенно {len(deleted)} сообщений участником {inter.user}")

            embed = disnake.Embed(
                title="Успешное использование команды **clear**",
                description=f'Удалено {len(deleted)} сообщений',
                color=disnake.Colour.blurple()
            )
            await inter.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            logging.error(f"Ошибка в комманде clear: {e}")

    @commands.slash_command(name="ban", description="Админ комманда. Удаляет игрока из сервера без возможности зайти обратно")
    @ModerateProcessing.Check_permissions()
    async def ban(self, inter, member: disnake.Member, reason: str):
        try:
            user = inter.user
            ModerateProcessing.Check_permissions()
            cursor = self.conn.cursor()
            SQLProcessing.CheckEconomicalMember(self, member)
            cursor.execute("UPDATE users SET ban = ? WHERE id = ?", ("Есть", member.id))
            self.conn.commit()
            cursor.close()


            if member != user:
                logging.info(f"Забанен участник {member} участником {inter.user} по причине: {reason}")
                embed = disnake.Embed(
                    title="Успешное использование команды **ban**",
                    description=f'Игрок {inter.user} забанил игрока {member} по причине: {reason}',
                    color=disnake.Color.blurple()
                )
                await inter.response.send_message(embed=embed, ephemeral=True)
                await inter.guild.ban(member, reason=reason)
            else:
                embed = disnake.Embed(
                    title="Проблема использование команды **ban**",
                    description='Вы выбрали себя же что бы выполнить комманду Модерации',
                    color=disnake.Color.blurple()
                )
                await inter.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            logging.error(f"Ошибка в комманде ban: {e}")

    @commands.slash_command(name="unban", description="Розбанивает игрока на сервере")
    async def unban(self, inter, member: disnake.User = commands.Param(description="Выбирете участника для розбана. Указывайте <@айди участника>")):
        try:
            ModerateProcessing.Check_permissions()
            logging.info(f"Розбан участника {member} участником {inter.user}")

            cursor = self.conn.cursor()
            SQLProcessing.CheckEconomicalMember(self, member)
            cursor.execute("UPDATE users SET ban = ? WHERE id = ?", ("Нету", member.id))
            self.conn.commit()
            cursor.close()

            embed = disnake.Embed(
                title="Успешное использование команды **unban**",
                description=f'Игрок {inter.user} розбанил игрока {member}',
                color=disnake.Colour.blurple()
            )
            await inter.response.send_message(embed=embed, ephemeral=True)

            await inter.guild.unban(member)

        except Exception as e:
            logging.error(f"Ошибка в комманд unban: {e}")

    @commands.slash_command(name="kick", description="Кикает игрока из сервера")
    async def kick(self, inter, member: disnake.Member, reason: str):
        try:
            ModerateProcessing.Check_permissions()
            logging.info(f"Кикнут участник {member} участником {inter.user} по причнине: {reason}")

            cursor = self.conn.cursor()
            SQLProcessing.CheckEconomicalMember(self, member)
            cursor.execute("UPDATE users SET kick = ? WHERE id = ?", ("Есть", member.id))
            self.conn.commit()
            cursor.close()

            embed = disnake.Embed(
                title="Успешное использование команды **kick**",
                description=f'Игрок {inter.user} кикнул игрока {member}',
                color=disnake.Colour.blurple()
            )
            await inter.response.send_message(embed=embed, ephemeral=True)

            await inter.guild.kick(member, reason=reason)

        except Exception as e:
            logging.error(f"Ошибка в комманде kick: {e}")

    @commands.slash_command(name="mute", description="Запрещает участнику говорить")
    async def mute(self, inter, member: disnake.Member, reason: str, duration: commands.Range[int, 0, 43200] = commands.Param(description="Выбирете на сколько минут хотите выдать мут")):
        try:
            ModerateProcessing.Check_permissions()
            logging.info(f"Участник {member} был замучен участником {inter.user} по причине: {reason}")

            embed = disnake.Embed(
                title="Успешное использование команды **mute**",
                description=f'Игрок {inter.user} замутил игрока {member} по причине {reason} на {duration} минут',
                color=disnake.Colour.blurple()
            )
            await inter.response.send_message(embed=embed, ephemeral=True)

            duration = datetime.datetime.now() + datetime.timedelta(minutes=int(duration))
            await member.timeout(reason=reason, until=duration)

            cursor = self.conn.cursor()
            SQLProcessing.CheckEconomicalMember(self, member)
            cursor.execute("UPDATE users SET mute = ? WHERE id = ?", ("Есть", member.id))
            self.conn.commit()
            cursor.close()

        except Exception as e:
            logging.error(f"Ошибка в комманде mute: {e}")