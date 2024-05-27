import disnake
from disnake.ext import commands
import random as r
import logging
import time
from Data_processing import CooldownProcessing, SQLProcessing

class EconomicCommands(commands.Cog):
    def __init__(self, bot: commands.Bot, conn):
        self.bot = bot
        self.conn = conn

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

    @commands.slash_command(
            name="dailybonus",
            description="Ежедневный бонус"
    )
    @commands.cooldown(1, 86400, commands.BucketType.member)
    async def DailyBonus(self, inter):
        try:
            user = inter.user
            amount = r.randint(100, 1000)
            logging.info(f"Участник {user.global_name} использовал комманду 'dailybonus' и получил {amount} 🌕")

            cursor = self.conn.cursor()
            SQLProcessing.CheckEconomicalUser(self, user)
            cursor.execute("UPDATE users SET cash = cash + ? WHERE id = ?", (amount, user.id))
            self.conn.commit()
            cursor.close()

            await inter.send(embed=disnake.Embed(
                title="Ежедневный бонус выдан!",
                description=f"Спасибо что использовали ежедневную комманду {user.global_name}! Вы получили {amount} 🌕.",
                color=disnake.Colour.og_blurple()
            ))

        except Exception as e:
            logging.error(f"Ошибка в комманде dailybonus: {e}")

    @commands.slash_command(
            name="classes",
            description="Senior: 25k🌕, Middle: 15k🌕, Junior: 10k🌕"
    )
    async def classes(self, inter, classes: str = commands.Param(description="Выберите класс для покупки.", choices=["Senior", "Middle", "Junior"])):
        try:
            user = inter.user
            logging.info(f"Участник {user.global_name} использовал комманду 'classes'")

            cursor = self.conn.cursor()
            SQLProcessing.CheckEconomicalUser(self, user)
            profile_data = cursor.execute("SELECT cash, rep, lvl, ecclass, job FROM users WHERE id = ?", (user.id,))
            profile_data = cursor.fetchone()

            for ecclass, cost, mult in [["Senior", 25000, 3], ["Middle", 15000, 2], ["Junior", 7500, 1.5]]:
                if classes == ecclass:  # Если класс совпадает с текущим классом из списка
                    if profile_data[0] >= cost:  # Если у пользователя достаточно лун для покупки класса
                        cursor.execute("UPDATE users SET ecclass = ? WHERE id = ?", (classes, user.id))
                        logging.info(f"Участник {user.global_name} использовал комманду 'classes' и купил класс {classes} за {cost} 🌕")
                        cursor.execute("UPDATE users SET cash = cash - ? WHERE id = ?", (cost, user.id))
                        self.conn.commit()
                        cursor.close()

                        await inter.send(embed=disnake.Embed(
                            title=f"Вы успешно купили класс {classes}!",
                            description=f"Теперь у вас есть x{mult} лун для работы 'Программист, 3D Дизайнер, 2D Дизайнер'",
                            color=disnake.Colour.og_blurple()
                        ))

                    else:
                        await inter.send(embed=disnake.Embed(
                            title="Проблема в использовании команды **classes**",
                            description=f"У вас недостаточно лун для покупки класса {classes}",
                            color=disnake.Colour.og_blurple()
                        ))
                    return
                
        except Exception as e:
            logging.error(f"Ошибка в комманде classes: {e}")

    @commands.slash_command(
            name="job",
            description="при использовании исполняет вашу работу. Работает раз в 8 часов"
    )

    @commands.cooldown(1, (28800), commands.BucketType.user)
    async def job(self, inter, job: str = commands.Param(description='Выберите работу на которой будете работать.', choices=['Программист', '3D Дизайнер', '2D Дизайнер', 'Строитель', 'Подработка', 'Косметолог', 'Столяр', 'Бухгалтер'])):
        try:
            user = inter.user

            cursor = self.conn.cursor()
            SQLProcessing.CheckEconomicalUser(self, user)
            profile_data = cursor.execute("SELECT cash, rep, lvl, ecclass, job FROM users WHERE id = ?", (user.id,))
            profile_data = cursor.fetchone()

            if job != profile_data[4]:
                await inter.send(embed=disnake.Embed(
                    title="Проблема в использовании комманды **job**",
                    description=f"Вы не можете выбрать работу которой нету у вас в профиле! Если у вас отсутствует работа тогда выберите 'Подработка'",
                    color=disnake.Colour.og_blurple()
                ))
                return
                
            
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

                    cursor.execute("UPDATE users SET cash = cash + ?, rep = rep + ? WHERE id = ?", (amount, amount_rep, user.id))
                    self.conn.commit()
                    cursor.close()

                    logging.info(f"Участник {user.global_name} использовал комманду 'job' и зароботал {amount} 🌕")

                    await inter.send(embed=disnake.Embed(
                        title="Вы успешно поработали!",
                        description=f"Спасибо что поработали в сфере {job}! За эти 8 часов работы вы получили {amount} 🌕. Так же вы получили {amount_rep} репутации. Вам нужно отдохнуть поэтому у вас кулдаун на комманду 8 часов",
                        color=disnake.Colour.og_blurple()
                    ))
    
        except Exception as e:
            logging.error(f"Ошибка в комманде job: {e}")

    @commands.slash_command(
        name="send",
        description="Отправляет деньги другому игроку"
    )
    async def send(self, inter, member: disnake.Member, amount: commands.Range[int, 0, 10000] = commands.Param(description="Выберите сумму которую хотите отправить")):
        try:
            user = inter.user
            logging.info(f"Участник {user.global_name} отправил игроку {member.global_name}, {amount} 🌕")

            cursor = self.conn.cursor()
            SQLProcessing.CheckEconomicalMember(self, member)
            SQLProcessing.CheckEconomicalUser(self, user)
            user_data = cursor.execute("SELECT cash, rep, lvl, ecclass, job FROM users WHERE id = ?", (user.id,))  # user its member who use the command
            user_data = cursor.fetchone()

            if user.id == member.id:  # If user send money for himself
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
            
            cursor.execute("UPDATE users SET cash = cash + ? WHERE id = ?", (amount, member.id))
            cursor.execute("UPDATE users SET cash = cash - ? WHERE id = ?", (amount, user.id))
            self.conn.commit()
            cursor.close()

            await inter.send(embed=disnake.Embed(
                title="Деньги отправлены успешно!",
                description=f"Вы отправили {member.global_name} сумму в {amount} 🌕",
                color=disnake.Colour.og_blurple()
            ))

        except Exception as e:
            logging.error(f"Ошибка в комманде send: {e}")

    #Command "Profile"

    @commands.slash_command(
            name="profile",
            description="Открывает профиль игрока"
    )
    async def profile(self, inter, member: disnake.Member):
        try:
            logging.info(f"Был просмотрен профиль игрока {member.global_name}")

            cursor = self.conn.cursor()
            SQLProcessing.CheckEconomicalMember(self, member)
            profile_data = cursor.execute("SELECT cash, rep, lvl, ecclass, job FROM users WHERE id = ?", (member.id,))
            profile_data = cursor.fetchone()

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

            self.conn.commit()
            cursor.close()

        except Exception as e:
            logging.error(f"Ошибка в комманде profile: {e}")