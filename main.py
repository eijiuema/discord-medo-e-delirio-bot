import os
import discord
import asyncio
from dotenv import load_dotenv
from discord.ext import commands
from cogs.virgulas import Virgulas
from cogs.musicas import Musicas

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

bot = commands.Bot(command_prefix=commands.when_mentioned_or(","), intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

@bot.command(aliases=["s"])
async def stop(ctx: commands.Context):
    await ctx.voice_client.disconnect()

async def main():
    async with bot:
        await bot.add_cog(Virgulas(bot))
        await bot.add_cog(Musicas(bot))
        await bot.start(os.getenv("TOKEN"))


asyncio.run(main())