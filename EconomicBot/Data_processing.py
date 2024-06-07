import disnake
from disnake.ext import commands
import random as r
import sqlite3

class SQLProcessing():
        def __init__(self, bot: commands.Bot, conn):
            self.bot = bot
            self.conn = conn

        def CheckEconomicalMember(self, member):
            cursor = self.conn.cursor()
            member_data = cursor.execute("SELECT cash, rep, lvl, ecclass, job, inventory, ban, mute FROM users WHERE id = ?", (member.id,))  # mention member\
            member_data = cursor.fetchone()
            if member_data is None:
                cursor.execute("INSERT INTO users(name, id, cash, rep, lvl, ecclass, job, inventory, ban, mute, kick) VALUES (?, ?, 0, 0, 1, ?, ?, ?, ?, ?, ?)", (str(member), member.id, "Отсутствует", "Подработка", "Ничего", "Нету", "Нету", "Нету"))

        def CheckLvlMember(self, member):
            cursor = self.conn.cursor()
            cursor.execute("SELECT rep, lvl FROM users WHERE id = ?", (member.id,))
            LvlDataLoading = cursor.fetchone()
            rep, lvl = LvlDataLoading
    
            level_up = 1 * lvl**2 + 15 * lvl + 15
            while rep >= level_up:
                lvl += 1
                level_up = 1 * lvl**2 + 15 * lvl + 15

            cursor.execute("UPDATE users SET lvl = ? WHERE id = ?", (lvl, member.id))
            self.conn.commit()
            cursor.close()

class ModerateProcessing():
    @staticmethod
    def Check_permissions():
        def predicate(inter):
            if not inter.guild.me.guild_permissions.ban_members or not inter.guild.me.guild_permissions.manage_messages:
                embed = disnake.Embed(
                    title="Проблема в использовании команд Модерации",
                    description='У вас нет прав на использование этой команды',
                    color=disnake.Color.blurple()
                )
                return False
            return True
        return commands.check(predicate)

class Job():
    jobs_list = [
        {"name": "3D Дизайнер", "min": 500, "max": 1500, "rep": 6, "buy": 90},
        {"name": "Программист", "min": 1000, "max": 3000, "rep": 10, "buy": 150},
        {"name": "2D Дизайнер", "min": 750, "max": 2000, "rep": 7, "buy": 105},
        {"name": "Строитель", "min": 1000, "max": 2500, "rep": 6, "buy": 75},
        {"name": "Подработка", "min": 500, "max": 1000, "rep": 5, "buy": 0},
        {"name": "Косметолог", "min": 750, "max": 2000, "rep": 8, "buy": 120},
        {"name": "Столяр", "min": 1250, "max": 2750, "rep": 9, "buy": 135},
        {"name": "Бухгалтер", "min": 750, "max": 2000, "rep": 7, "buy": 105},
        {"name": "Стример", "min": 1500, "max": 4000, "rep": 12, "buy": 180},
        {"name": "Ютубер", "min": 1000, "max": 2350, "rep": 11, "buy": 165}
    ]

    @staticmethod
    def Multiplier(min_amount, max_amount, job, classes):
        amount = r.randint(min_amount, max_amount)
        if job == 'Программист' and classes == "Senior":
            amount *= 3
        elif classes == "Middle":
            amount *= 2
        elif classes == "Junior":
            amount *= 1.5
        return amount
    
class Embed():
        def author(embed, member):
            embed.set_author(
                name=member.global_name,
                icon_url=member.display_avatar,
            )

class ShopsConfig():
    class Jobs():
        def List(embed):
            embed.add_field(name=" • 3D Дизайнер", value="• Не лёгкая работа \n" + f"Репутация: ``90`` |\n Доход: ``500-1500``", inline=True)
            embed.add_field(name=" • Программист", value="• Интересные люди \n" + f"Репутация: ``150`` |\n Доход: ``1000-3000``", inline=True)
            embed.add_field(name=" • 2D Дизайнер", value="• 2D дизайн это круто! \n" + f"Репутация: ``105`` |\n Доход: ``750-2000``", inline=True)
            embed.add_field(name=" • Строитель", value="• Кирпичики это имба! \n" + f"Репутация: ``75`` |\n Доход: ``1000-2500``", inline=True)
            embed.add_field(name=" • Косметолог", value="• Ой девочки я в шоке \n" + f"Репутация: ``120`` |\n Доход: ``750-2000``", inline=True)
            embed.add_field(name=" • Столяр", value="• Робота очень сложная! \n" + f"Репутация: ``135`` |\n Доход: ``1250-2750``", inline=True)
            embed.add_field(name=" • Бухгалтер", value="• 20 часов в Excel :< \n" + f"Репутация: ``105`` |\n Доход: ``750-2000``", inline=True)
            embed.add_field(name=" • Стример", value="• Ого! А скинь свой твич \n" + f"Репутация: ``180`` |\n Доход: ``1500-4000``", inline=True)
            embed.add_field(name=" • Ютубер", value="• Лучше чем стример \n" + f"Репутация: ``165`` |\n Доход: ``1000-2350``", inline=True)

    class Classes():
        def List(embed):
            embed.add_field(name=" • Senior", value="• Похвально! \n" + f"Цена: ``25000`` |\n Репутация: ``x3`` \n Доход: ``x3``", inline=True)
            embed.add_field(name=" • Middle", value="• Пойдёт! \n" + f"Цена: ``15000`` |\n Репутация: ``x2.5`` \n Доход: ``x2``", inline=True)
            embed.add_field(name=" • Junior", value="• Главное что бы нравилось! \n" + f"Цена: ``10000`` |\n Репутация: ``x2`` \n Доход: ``x1.5``", inline=True)

        class_list = [
            {"name": "3D Дизайнер", "cost": 25000},
            {"name": "Программист", "cost": 15000},
            {"name": "2D Дизайнер", "cost": 10000}
        ]
    
    class Donate():
        def List(embed):
            embed.add_field(name="Comming Soon", value=" ", inline=True)

    class CustomRole():
        def List(embed):
            embed.add_field(name="Comming Soon", value=" ", inline=True)

class Buy_things():
        def ClassCost(ClassList):
            for classes_info in ClassList: # ShopsConfig.Classes.class_list()
                ClassesCost = classes_info["cost"]
                return ClassesCost
        def JobCost(JobList):
            for jobs_info in JobList: # Job.jobs_list()
                JobsCost = jobs_info["buy"]
                return JobsCost

        def EmbedNone():
            disnake.Embed(
                title="Проблема в использовании комманды **buy_things",
                description=f"Вы пропустили выбор",
                color=disnake.Colour.og_blurple()
            )
