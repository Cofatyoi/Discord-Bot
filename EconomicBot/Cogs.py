from os import listdir

def load_cog(bot, conn) -> None:  # ignore: W0613
    for filename in listdir("./cogs"):
        if filename.endswith('.py'):
            file: str = filename[:-3]
            exec(f"from cogs.{file} import {file}")
            exec(f"bot.add_cog({file}(bot, conn))")