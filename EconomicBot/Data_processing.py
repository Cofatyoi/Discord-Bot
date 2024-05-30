import disnake
from disnake.ext import commands
import sqlite3

class SQLProcessing():
        def __init__(self, bot: commands.Bot, conn):
            self.bot = bot
            self.conn = conn

        def CheckEconomicalUser(self, user_id):
            cursor = self.conn.cursor()
            profile_data = cursor.execute("SELECT cash, rep, lvl, ecclass, job, inventory, ban, mute, kick FROM users WHERE id = ?", (user_id.id,))
            profile_data = cursor.fetchone()
            if profile_data is None:
                cursor.execute("INSERT INTO users(name, id, cash, rep, lvl, ecclass, job, inventory, ban, mute, kick) VALUES (?, ?, 0, 0, 1, ?, ?, ?, ?, ?, ?)", (str(user_id), user_id.id, "Отсутствует", "Подработка", "Ничего", "Нету", "Нету", "Нету"))
        def CheckEconomicalMember(self, member):
            cursor = self.conn.cursor()
            member_data = cursor.execute("SELECT cash, rep, lvl, ecclass, job, inventory, ban, mute, FROM users WHERE id = ?", (member.id,))  # mention member\
            member_data = cursor.fetchone()
            if member_data is None:
                cursor.execute("INSERT INTO users(name, id, cash, rep, lvl, ecclass, job, inventory, ban, mute, kick) VALUES (?, ?, 0, 0, 1, ?, ?, ?, ?, ?, ?)", (str(member), member.id, "Отсутствует", "Подработка", "Ничего", "Нету", "Нету", "Нету"))
        def CheckLvlMember(self, rep):
            cursor = self.conn.cursor()
            LvlDataLoading = cursor.execute("SELECT rep, lvl FROM users WHERE id = ?", (member.id,))
            

class CooldownProcessing():
    @commands.Cog.listener()
    async def on_slash_command_error(self, inter, error):
        if isinstance(error, commands.CommandOnCooldown):
            seconds = error.retry_after
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            embed = disnake.Embed(
                title='Команда на задержке.',
                description=f'Следующее использование команды будет доступно через `{int(hours)} часов, {int(minutes)} минут, {int(seconds)} секунд`',
                colour=disnake.Colour.blurple()
            )
            await inter.send(embed=embed, ephemeral=True)

class ModerateProcessing():
        def Check_permissions():
            @commands.has_permissions(administrator=True)
            async def predicate(inter):
                if not inter.guild.me.guild_permissions.manage_messages:
                    embed = disnake.Embed(
                        title="Проблема в использовании комманд Модерации",
                        description=f'У вас нету прав на использование этой комманды',
                        color=disnake.Colour.og_blurple()
                    )
                    await inter.response.send_message(embed=embed, ephemeral=True)
                    return False
                return True
            return commands.check(predicate)