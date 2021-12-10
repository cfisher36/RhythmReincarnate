<<<<<<< HEAD
"""
This is compressed into one file.
"""

#HELLO. I AM UPDATED VIA GIT. AGAIN.

=======
>>>>>>> 19559c387b1f74c3ef6e112c790746a80c86b3a8
import asyncio
import youtube_dl
import pafy
import discord
from discord.ext import commands

class Player(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}

        self.setup()

    def setup(self):
        for guild in self.bot.guilds:
            self.song_queue[guild.id] = []

    async def check_queue(self, ctx):
        #bug when trying to play after initial song finishes
        if len(self.song_queue[ctx.guild.id]) > 0:
            await self.play_song(ctx, self.song_queue[ctx.guild.id][0])
            self.song_queue[ctx.guild.id].pop(0)
        #empty song queue location?

    async def search_song(self, amount, song, get_url=False):
        info = await self.bot.loop.run_in_executor(None, lambda: youtube_dl.YoutubeDL({"format" : "bestaudio", "quiet" : True}).extract_info(f"ytsearch{amount}:{song}", download=False, ie_key="YoutubeSearch"))
        if len(info["entries"]) == 0: return None

        return [entry["webpage_url"] for entry in info["entries"]] if get_url else info

    async def play_song(self, ctx, song):
        url = pafy.new(song).getbestaudio().url
        ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url)), after=lambda error: self.bot.loop.create_task(self.check_queue(ctx)))
        ctx.voice_client.source.volume = 0.5
        #empty song queue location?

    @commands.command()
    async def join(self,ctx):
        if ctx.author.voice is None:
            return await ctx.send("Get yo dumbass in the channel.")
            
        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()

        await ctx.author.voice.channel.connect()

    @commands.command()
    async def leave(self,ctx):
        if ctx.voice_client is not None:
            return await ctx.voice_client.disconnect()

        await ctx.send("I don't know what I'm doing here. Let me in. LET ME INNNN!")

    @commands.command()
    async def play(self, ctx, *, song=None):
        if song is None:
            return await ctx.send("Gimme something to play, dumbass.")

        if ctx.voice_client is None:
            return await ctx.send("I don't know what I'm doing here. Let me in. LET ME INNNN!")
            #maybe add connect command

        if not ("youtube.com/watch?" in song or "https://youtu.be/" in song):
            await ctx.send("Searching. . .")

            result = await self.search_song(1, song, get_url=True)

            if result is None:
                return await ctx.send("Does that song really exist? Try the search command.")

            song = result[0]

        if ctx.voice_client.source is not None:
            queue_len = len(self.song_queue[ctx.guild.id])

            if queue_len < 10 and queue_len != 0:
                self.song_queue[ctx.guild.id].append(song)
                return await ctx.send(f"Oi, we got a song coming up at position: {queue_len+1}.")

            elif queue_len >= 10:
                return await ctx.send("You're overloading me! Calm down and wait for the current song to end.")

        await self.play_song(ctx, song)
        #empty song queue location?
        await ctx.send(f"Now playing: {song}")

    @commands.command()
    async def search(self, ctx, *, song=None):
        if song is None: return await ctx.send("I need a song to search, dumbass...")

        await ctx.send("Searching for song...")

        info = await self.search_song(5, song)

        embed = discord.Embed(title=f"Results for '{song}':", description= "*Pick a card, any card.*\n", colour=discord.Colour.red())

        amount = 0
        for entry in info["entries"]:
            embed.description += f"[{entry['title']}]({entry['webpage_url']})\n"
            amount += 1

        embed.set_footer(text = f"Displaying the first {amount} results.")
        await ctx.send(embed=embed)

    @commands.command()
    async def queue(self, ctx):
        if len(self.song_queue[ctx.guild.id]) == 0:
            return await ctx.send("There are no songs in the queue, dumbass.")

        embed = discord.Embed(title="Song Queue", description="", colour=discord.Colour.dark_gold())
        i = 1
        for url in self.song_queue[ctx.guild.id]:
            embed.description += f"{i}) {url}\n"

            i += 1

        embed.set_footer(text="There they are. Happy?")
        await ctx.send(embed=embed)

    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send("Gimme a song to play, dumbass.")

        if ctx.author.voice is None:
            return await ctx.send("Get in a channel, dumbass.")

        if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            return await ctx.send("Trying to play a song in another channel? Good try. Denied by precedent of haram.")

        poll = discord.Embed(title=f"Vote to Skip Song by - {ctx.author.name}", description="**75% must vote to skip for this to pass. Cole's vote doesn't count. Democracy is dead.**", colour=discord.Colour.blue())
        poll.add_field(name="Skip", value=":white_check_mark:")
        poll.add_field(name="Stay", value=":no_entry_sign:")
        poll.set_footer(text="Voting ends in 15 seconds.")

        poll_msg = await ctx.send(embed=poll)
        poll_id = poll_msg.id

        await poll_msg.add_reaction(u"\u2705")
        await poll_msg.add_reaction(u"\U0001F6AB")

        #edit countdown by loop asyncio.sleep(1) and edit footer
        await asyncio.sleep(15)

        poll_msg = await ctx.channel.fetch_message(poll_id)

        votes = {u"\u2705": 0, u"\U0001F6AB": 0}
        reacted = []

        for reaction in poll_msg.reactions:
            if reaction.emoji in [u"\u2705", u"\U0001F6AB"]:
                async for user in reaction.users():
                    if user.voice.channel.id == ctx.voice_client.channel.id and user.id not in reacted and not user.bot:
                        votes[reaction.emoji] += 1

                        reacted.append(user.id)

        skip = False

        if votes[u"\u2705"] > 0:
            if votes[u"\U0001F6AB"] == 0 or votes[u"\u2705"] / (votes[u"\u2705"] + votes[u"\U0001F6AB"]) >= 0.75:
                skip = True
                embed = discord.Embed(title="Skip Successful", description="***Skipping the current song now.***", colour=discord.Colour.green())

        if not skip:
            embed = discord.Embed(title="Skip Failed", description="***You will listen to this song, and you will like it.***", colour=discord.Colour.dark_red())

        embed.set_footer(text="Voting has ended. Hope you're happy with the results. Losers will be publicly executed on sight.")

        await poll_msg.clear_reactions()
        await poll_msg.edit(embed=embed)

        if skip:
            ctx.voice_client.stop()
