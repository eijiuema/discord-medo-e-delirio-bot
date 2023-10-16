import json
import discord
from thefuzz import fuzz
from discord.ext import commands
from unidecode import unidecode

with open("files/sound_data.json", "r", encoding="utf-8") as sound_data_file:
    sounds = json.load(sound_data_file)


def scorer(query, data):
    score = max(
        fuzz.WRatio(unidecode(query).lower(), unidecode(data["title"]).lower(), force_ascii=False),
        fuzz.WRatio(unidecode(query).lower(), unidecode(data["description"]).lower(), force_ascii=False),
        fuzz.WRatio(unidecode(query).lower(), unidecode(data["filename"]).lower(), force_ascii=False),
    )
    return (score, data)


def get_sound_by_id(id: str):
    return next(filter(lambda sound: sound["id"] == id, sounds))


def get_sounds(query: str):
    matches = [scorer(query, sound) for sound in sounds]
    sorted_matches = sorted(matches, key=lambda match: match[0], reverse=True)
    sorted_sounds = [match[1] for match in sorted_matches]
    return sorted_sounds


class Virgulas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["v"])
    async def virgula(self, ctx: commands.Context, *, query: str):
        """Retorna um dropdown com opções de vírgulas para tocar"""
        sounds = get_sounds(query)
        if len(sounds) == 0:
            await ctx.reply(
                "Tá inventando vírgula ai? (Não encontramos essa vírgula)",
                ephemeral=True,
            )
            return
        await ctx.reply(view=DropdownSoundView(sounds=sounds[:5]), ephemeral=True)


class DropdownSound(discord.ui.Select):
    def __init__(self, sounds):
        options = [
            discord.SelectOption(
                label=sound["title"],
                value=sound["id"]
            )
            for sound in sounds
        ]
        super().__init__(
            placeholder="Selecione uma opção",
            max_values=1,
            min_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.guild.voice_client is None:
            await interaction.user.voice.channel.connect()
        else:
            await interaction.guild.voice_client.move_to(interaction.user.voice.channel)
            
        voice = interaction.guild.voice_client

        sound = get_sound_by_id(self.values[0])
        file = f'files/sounds/{sound["filename"]}'
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(file), volume=0.6)
        voice.play(source)
        await interaction.response.send_message(f'Reproduzindo: {sound["title"]}', ephemeral=True)


class DropdownSoundView(discord.ui.View):
    def __init__(self, *, timeout=30, sounds):
        super().__init__(timeout=timeout)
        self.add_item(DropdownSound(sounds))
