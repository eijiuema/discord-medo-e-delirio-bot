import json
import discord
from thefuzz import fuzz
from discord.interactions import Interaction
from discord.ext import commands
import datetime

with open("files/song_data.json", "r", encoding="utf-8") as song_data_file:
    songs = json.load(song_data_file)


def scorer(query, data):
    score = max(
        fuzz.WRatio(query, data["title"]),
        fuzz.WRatio(query, data["description"]),
        fuzz.WRatio(query, data["filename"]),
    )
    return (score, data)


def get_song_by_id(id: str):
    return next(filter(lambda song: song["id"] == id, songs))


def get_songs(query: str):
    matches = [scorer(query, song) for song in songs]
    sorted_matches = sorted(matches, key=lambda match: match[0], reverse=True)
    sorted_songs = [match[1] for match in sorted_matches]
    return sorted_songs


class Musicas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["m"])
    async def musica(self, ctx: commands.Context, *, query: str):
        """Retorna um dropdown com opções de músicas para tocar"""
        songs = get_songs(query)
        if len(songs) == 0:
            await ctx.reply(
                "Tá inventando música ai? (Não encontramos essa música)",
                ephemeral=True,
            )
            return
        await ctx.reply(view=DropdownsongView(songs=songs[:5]), ephemeral=True)


class Dropdownsong(discord.ui.Select):
    def __init__(self, songs):
        options = [
            discord.SelectOption(
                label=f'{song["title"]} - {str(datetime.timedelta(seconds=round(song["duration"])))}',
                value=song["id"],
                description=song["description"],
            )
            for song in songs
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

        song = get_song_by_id(self.values[0])
        file = f'files/songs/{song["filename"]}'
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(file), volume=0.6)
        voice.play(source)
        await interaction.response.send_message(
            f'Reproduzindo: {song["title"]}', ephemeral=True
        )


class DropdownsongView(discord.ui.View):
    def __init__(self, *, timeout=30, songs):
        super().__init__(timeout=timeout)
        self.add_item(Dropdownsong(songs))
