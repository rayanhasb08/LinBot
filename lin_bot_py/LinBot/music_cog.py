from ast import alias
import discord
from discord.ext import commands

from youtube_dl import YoutubeDL


class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # all the music related stuff
        self.is_playing = False
        self.is_paused = False

        # 2d array containing [song, channel]
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                               'options': '-vn'}

        self.vc = None

    # searching the item on youtube
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception:
                return False

        return {'source': info['formats'][0]['url'], 'title': info['title']}

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            # get the first url
            m_url = self.music_queue[0][0]['source']

            # remove the first element as you are currently playing it
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    # infinite loop checking
    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']

            # try to connect to voice channel if you are not already connected
            if self.vc is None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                # in case we fail to connect
                if self.vc is None:
                    await ctx.send("Could not connect to the voice channel")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])

            # remove the first element as you are currently playing it
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    @commands.command(name="play", aliases=["p", "playing"], help="Plays a selected song from youtube")
    async def play(self, ctx, *args):
        global voice_channel
        query = " ".join(args)

        if ctx.author.voice is None:
            # you need to be connected so that the bot knows where to go
            await ctx.send("""``` Connecte toi a un channel ```""")
        elif self.vc is not None:
            voice_channel = ctx.author.voice.channel
            if self.vc.channel is not voice_channel:
                await ctx.send("""``` Bot d??j?? connecter sur un serveur, prochaine update pour que ??a marche quand m??me ```""")
            elif self.is_paused:
                self.vc.resume()
            else:
                voice_channel = ctx.author.voice.channel
                song = self.search_yt(query)
                if type(song) == type(True):
                    await ctx.send(
                        """``` Could not download the song. Incorrect format try another keyword. This could be due to playlist or a livestream format. ```""")
                else:
                    await ctx.send(f"""```Song {str(song['title'])} is added to the queue```""")
                    self.music_queue.append([song, voice_channel])

                    if self.is_playing is False:
                        await self.play_music(ctx)
        elif self.is_paused:
            self.vc.resume()
        else:
            voice_channel = ctx.author.voice.channel
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send(
                    """```Could not download the song. Incorrect format try another keyword. This could be due to playlist or a livestream format.```""")
            else:
                await ctx.send(f"""```Song {str(song['title'])} is added to the queue```""")
                self.music_queue.append([song, voice_channel])

                if self.is_playing is False:
                    await self.play_music(ctx)

    @commands.command(name="pause", help="Pauses the current song")
    async def pause(self, ctx, *args):
        if ctx.author.voice is None:
            # you need to be connected so that the bot knows where to go
            await ctx.send("""``` Connecte toi a un channel ``` """)
            return
        elif self.vc is not None:
            voice_channel = ctx.author.voice.channel
            if self.vc.channel is not voice_channel:
                await ctx.send(
                    """``` Bot d??j?? connecter sur un serveur, prochaine update pour que ??a marche quand m??me ``` """)
                return
            else:
                if self.is_playing:
                    self.is_playing = False
                    self.is_paused = True
                    await ctx.send("""``` Music paused ``` """)
                    self.vc.pause()
                elif self.is_paused:
                    await ctx.send("""``` Music resumed ``` """)
                    self.vc.resume()

    @commands.command(name="resume", aliases=["r"], help="Resumes playing")
    async def resume(self, ctx, *args):
        if ctx.author.voice is None:
            # you need to be connected so that the bot knows where to go
            await ctx.send("""``` Connecte toi a un channel ``` """)
            return
        elif self.vc is not None:
            voice_channel = ctx.author.voice.channel
            if self.vc.channel is not voice_channel:
                await ctx.send("""``` Bot d??j?? connecter sur un serveur, prochaine update pour que ??a marche quand m??me ``` """)
                return
        if self.is_paused:
            await ctx.send("""``` Music resumed ``` """)
            self.vc.resume()

    @commands.command(name="skip", aliases=["s"], help="Skips the current song")
    async def skip(self, ctx):
        if ctx.author.voice is None:
            # you need to be connected so that the bot knows where to go
            await ctx.send("""``` Connecte toi a un channel ``` """)
            return
        elif self.vc is not None:
            voice_channel = ctx.author.voice.channel
            if self.vc.channel is not voice_channel:
                await ctx.send(
                    """``` Bot d??j?? connecter sur un serveur, prochaine update pour que ??a marche quand m??me ``` """)
                return
        if self.vc is not None and self.vc:
            await ctx.send("""``` Music skipped ``` """)
            self.vc.stop()
            # try to play next in the queue if it exists
            await self.play_music(ctx)

    @commands.command(name="queue", aliases=["q"], help="Displays the current songs in queue")
    async def queue(self, ctx):
        if ctx.author.voice is None:
            # you need to be connected so that the bot knows where to go
            await ctx.send("""``` Connecte toi a un channel ``` """)
            return
        elif self.vc is not None:
            voice_channel = ctx.author.voice.channel
            if self.vc.channel is not voice_channel:
                await ctx.send(
                    """``` Bot d??j?? connecter sur un serveur, prochaine update pour que ??a marche quand m??me ``` """)
                return
        music_list = ""
        for i in range(0, len(self.music_queue)):
            music_list += self.music_queue[i][0]['title'] + "\n"

        if music_list != "":
            await ctx.send(f"""``` {str(music_list)} ```""")
        else:
            await ctx.send("""``` No music in queue ```""")

    @commands.command(name="clear", aliases=["c", "bin"], help="Stops the music and clears the queue")
    async def clear(self, ctx):
        if ctx.author.voice is None:
            # you need to be connected so that the bot knows where to go
            await ctx.send("""``` Connecte toi a un channel ``` """)
            return
        elif self.vc is not None:
            voice_channel = ctx.author.voice.channel
            if self.vc.channel is not voice_channel:
                await ctx.send(
                    """``` Bot d??j?? connecter sur un serveur, prochaine update pour que ??a marche quand m??me ``` """)
                return
        if self.vc is not None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("""``` Music queue cleared ````""")

    @commands.command(name="leave", aliases=["disconnect", "l", "d"], help="Kick the bot from VC")
    async def dc(self, ctx):
        if ctx.author.voice is None:
            # you need to be connected so that the bot knows where to go
            await ctx.send("""``` Connecte toi a un channel ``` """)
            return
        elif self.vc is not None:
            voice_channel = ctx.author.voice.channel
            if self.vc.channel is not voice_channel:
                await ctx.send(
                    """``` Bot d??j?? connecter sur un serveur, prochaine update pour que ??a marche quand m??me ``` """)
                return
        self.is_playing = False
        self.is_paused = False
        await ctx.send("""``` Ok bye ```""")
        await self.vc.disconnect()
        self.vc = None
