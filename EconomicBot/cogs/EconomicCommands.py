import disnake
from disnake.ext import commands
import random as r
import logging
from Data_processing import SQLProcessing, Job, Embed, ShopsConfig, Buy_things

logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="a", encoding='utf-8', format="%(asctime)s %(levelname)s %(message)s")

class EconomicCommands(commands.Cog, disnake.ui.View):
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

    @commands.slash_command(name="dailybonus", description="Ежедневный бонус")
    @commands.cooldown(1, 86400, commands.BucketType.member)
    async def DailyBonus(self, inter):
        try:
            user = inter.user
            amount = r.randint(100, 1000)
            logging.info(f"Участник {user.global_name} использовал комманду 'dailybonus' и получил {amount} 🌕")

            cursor = self.conn.cursor()
            SQLProcessing.CheckEconomicalMember(self, member=user)
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

    @commands.slash_command(name="buy_things", description="Позволяет купить вещи из меню /shop")
    async def buy_things(self, inter, classes: str = commands.Param(description="Выберите класс для покупки. 'Skip' - для пропуска", choices=["Senior", "Middle", "Junior", "Skip"]), jobs: str = commands.Param(description="Выберите работу. 'Skip' - для пропуска", choices=["3D Дизайнер", "Программист", "2D Дизайнер", "Строитель", "Косметолог", "Столяр", "Бухгалтер", "Стример", "Ютубер", "Skip"])):
        try:
            user = inter.user
            logging.info(f"Участник {user.global_name} использовал комманду 'buy_things'")

            cursor = self.conn.cursor()
            SQLProcessing.CheckEconomicalMember(self, member=user)
            profile_data = cursor.execute("SELECT cash, rep, lvl, ecclass, job FROM users WHERE id = ?", (user.id,))
            profile_data = cursor.fetchone()
            ClassCost = Buy_things.ClassCost(ClassList=ShopsConfig.Classes.class_list)
            JobCost = Buy_things.JobCost(JobList=Job.jobs_list)

            if classes != "Skip":
                if ClassCost >= profile_data[0]:
                    cursor.execute("UPDATE users SET cash = cash - ?, ecclass = ? WHERE id = ?", (ClassCost, classes, user.id))
                    logging.info(f"Участник {user.global_name} приобрёл класс {classes} за {ClassCost} 🌕") 
                else:
                    await inter.send(embed=disnake.Embed(
                        title="Проблема в использовании комманды **buy_things**",
                        description=f"У вас недостаточно денег",
                        color=disnake.Colour.og_blurple()
                    ))
            else:
                return None
            
            if jobs != "Skip":
                if JobCost >= profile_data[1]:
                    cursor.execute("UPDATE users SET job = ? WHERE id = ?", (jobs, user.id))
                    logging.info(f"Участник {user.global_name} поставил себе работу {jobs} за {JobCost} 🌕") 
                else:
                    await inter.send(embed=disnake.Embed(
                        title="Проблема в использовании комманды **buy_things**",
                        description=f"У вас недостаточно репутации",
                        color=disnake.Colour.og_blurple()
                    ))
            else:
                return None

        except Exception as e:
            logging.error(f"Ошибка в комманде buy_things: {e}")

    @commands.slash_command(name="job", description="при использовании исполняет вашу работу. Работает раз в 8 часов")
    @commands.cooldown(1, (28800), commands.BucketType.user)
    async def job(self, inter, job: str = commands.Param(description='Выберите работу на которой будете работать.', choices=['Программист', '3D Дизайнер', '2D Дизайнер', 'Строитель', 'Подработка', 'Косметолог', 'Столяр', 'Бухгалтер'])):
        try:
            user = inter.user

            cursor = self.conn.cursor()
            SQLProcessing.CheckEconomicalMember(self, member=user)
            profile_data = cursor.execute("SELECT cash, rep, lvl, ecclass, job FROM users WHERE id = ?", (user.id,))
            profile_data = cursor.fetchone()

            if job != profile_data[4]:
                await inter.send(embed=disnake.Embed(
                    title="Проблема в использовании комманды **job**",
                    description=f"Вы не можете выбрать работу которой нету у вас в профиле! Если у вас отсутствует работа тогда выберите 'Подработка'",
                    color=disnake.Colour.og_blurple()
                ))
                return
                
            classes = profile_data[3]
            for job_info in Job.jobs_list:
                if job == job_info["name"]:
                    amount = Job.Multiplier(job_info["min"], job_info["max"], job, classes)
                    cursor.execute("UPDATE users SET cash = cash + ?, rep = rep + ? WHERE id = ?", (amount, job_info["rep"], user.id))
                    self.conn.commit()
                    cursor.close()

                    logging.info(f"Участник {user.global_name} использовал команду 'job' и заработал {amount} 🌕")

                    await inter.send(embed=disnake.Embed(
                        title="Вы успешно поработали!",
                        description=f"Спасибо, что поработали в сфере {job}! За эти 8 часов работы вы получили {amount} 🌕. Также вы получили {job_info['rep']} репутации. Вам нужно отдохнуть, поэтому у вас кулдаун на команду 8 часов.",
                        color=disnake.Colour.blurple()
                    ))
                    return
    
        except Exception as e:
            logging.error(f"Ошибка в комманде job: {e}")

    @commands.slash_command(name="send", description="Отправляет деньги другому игроку")
    async def send(self, inter, member: disnake.Member, amount: commands.Range[int, 0, 10000] = commands.Param(description="Выберите сумму которую хотите отправить")):
        try:
            user = inter.user
            logging.info(f"Участник {user.global_name} отправил игроку {member.global_name}, {amount} 🌕")

            cursor = self.conn.cursor()
            SQLProcessing.CheckEconomicalMember(self, member)
            SQLProcessing.CheckEconomicalMember(self, member=user)
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

    @commands.slash_command(name="profile", description="Открывает профиль игрока")
    async def profile(self, inter, member: disnake.Member):
        try:
            logging.info(f"Был просмотрен профиль игрока {member.global_name}")

            cursor = self.conn.cursor()
            SQLProcessing.CheckEconomicalMember(self, member)
            SQLProcessing.CheckLvlMember(self, member)
            profile_data = cursor.execute("SELECT cash, rep, lvl, ecclass, job FROM users WHERE id = ?", (member.id,))
            profile_data = cursor.fetchone()
            lvl = profile_data[2]
            level_up = 1 * lvl**2 + 15 * lvl + 15

            embed=disnake.Embed(
                title=f"Профиль пользователя **{member.global_name}**",
                color=disnake.Colour.og_blurple()
                )
            
            Embed.author(embed=embed, member=member)

            embed.add_field(name="**Информация**", value=f"``` Уровень: {profile_data[2]} | > {level_up} репутации```" + f"``` Репутация: {profile_data[1]} ```", inline=True)
            embed.add_field(name="**Экономика**", value=f"``` Баланс: {profile_data[0]} ```" + f"``` Работа: {profile_data[4]} ```" + f"``` Класс: {profile_data[3]} ```", inline=True)
            await inter.response.send_message(embed=embed)

            self.conn.commit()
            cursor.close()

        except Exception as e:
            logging.error(f"Ошибка в комманде profile: {e}")

    @commands.slash_command(name="shop", description="Открывает магазин покупок")
    async def shop(self, inter):
        try:
            options = [
                disnake.SelectOption(label="Classes", value="classes", description="Покупка классов"),
                disnake.SelectOption(label="Jobs", value="jobs", description="Выбор работ по уровню"),
                disnake.SelectOption(label="Donate", value="donate", description="Покупка донат валюты"),
                disnake.SelectOption(label="Custom Roles", value="customroles", description="Покупка кастомных ролей за игровые деньги!")
            ]

            Shops = disnake.ui.Select(
                placeholder="Выбор",
                options=options,
                min_values=1,
                max_values=1
            )
            view = disnake.ui.View()
            view.add_item(Shops)

            async def shop_callback(inter):
                selected_value = Shops.values[0]
                if selected_value == "classes":
                    embed = disnake.Embed(title="🙤━━━━━━━━━━━━━━━━┫⌜ КЛАССЫ ⌟┣━━━━━━━━━━━━━━━━🙦", color=disnake.Colour.og_blurple())
                    ShopsConfig.Classes.List(embed=embed)
                    await inter.response.edit_message(" ", embed=embed, view=view)

                elif selected_value == "jobs":
                    embed = disnake.Embed(title="🙤━━━━━━━━━━━━━━━━┫⌜ РАБОТЫ ⌟┣━━━━━━━━━━━━━━━━🙦", color=disnake.Colour.og_blurple())
                    ShopsConfig.Jobs.List(embed=embed)
                    await inter.response.edit_message(" ", embed=embed, view=view)

                elif selected_value == "donate":
                    embed = disnake.Embed(title="🙤━━━━━━━━━━━━━━━━┫⌜ ДОНАТ ⌟┣━━━━━━━━━━━━━━━━🙦", color=disnake.Colour.og_blurple())
                    ShopsConfig.Donate.List(embed=embed)
                    await inter.response.edit_message(" ", embed=embed, view=view)

                elif selected_value == "customroles":
                    embed = disnake.Embed(title="🙤━━━━━━━━━━━━┫⌜ КАСТОМНЫЕ РОЛИ ⌟┣━━━━━━━━━━━━🙦", color=disnake.Colour.og_blurple())
                    ShopsConfig.CustomRole.List(embed=embed)
                    await inter.response.edit_message(" ", embed=embed, view=view)
                
            Shops.callback = shop_callback

            await inter.response.send_message("Выбирете тип магазина для покупки", view=view)

        except Exception as e:
            logging.error(f"Ошибка в комманде shop: {e}")