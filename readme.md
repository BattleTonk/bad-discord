**A package that allows to make discord bots(DON'T USE IT, IT IS MADE FOR LEARNING PURPOSES, SHADY SHENANIGANS AND ALSO DOESN'T HAVE A DOCUMENTATION RIGHT NOW)**


Here is a simple echo bot
```python
from discord.bot import Bot


with open(".token") as token_file:
    token = token_file.read()
bot = Bot(token, debug_mode=True, self_bot=True)


@bot.event
async def message_create(msg):
    if !msg.author.isBot:
        msg.reply(msg.content)

bot.run_gateway()
