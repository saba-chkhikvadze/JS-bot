from discord.ext import commands
import youtube_dl
import discord

intents = discord.Intents.default()
intents.message_content = True

queues = {}

# ytdl = youtube_dl.YoutubeDL(ytdl_options)
client = commands.Bot(intents = intents, command_prefix='-')

def check_queue(ctx):
    server_id = ctx.guild.id
    if server_id not in queues or queues[server_id] == []:
        return
    vc = ctx.guild.voice_client
    src = queues[server_id].pop(0)
    vc.play(src, after = lambda x = None : check_queue(ctx))

def search_video(item):
    YDL_OPTIONS = {'format':"bestaudio"}
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ytdl:
        data = ytdl.extract_info(f'ytsearch:{item}', download=False)
        queried_data = data['entries'][0]
        url = queried_data['formats'][0]['url']
        title = queried_data['title']
        return url, title

async def make_source(url : str):
    source = None
    FFMPEG_OPTIONS = {'options':'-vn'}
    YDL_OPTIONS = {'format':"bestaudio"}
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['formats'][0]['url']
        source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
    return source

@client.event
async def on_ready():
    print('js bot running')

async def foo():
    print('done')
@commands.command()
async def play(ctx, title: str):
    vc = ctx.guild.voice_client
    server_id = ctx.guild.id
    channel = ctx.author.voice.channel
    if vc is None or not vc.is_connected():
        await channel.connect()
    vc = ctx.guild.voice_client
    url, video_title = search_video(title)
    if vc.is_playing():  
        new_source = await make_source(url=url)
        if new_source:
            if server_id in queues.keys():
                queues[server_id].append(new_source)
            else:
                queues[server_id] = [new_source]
            await ctx.send(f'{video_title} დაემატა რიგში')
            return
        else:
            await ctx.send('არასწორი ლინკი')
            return
    src = await make_source(url=url)
    vc.play(src, after = lambda x = None : check_queue(ctx))
client.add_command(play)

@commands.command()
async def resume(ctx):
    vc = ctx.guild.voice_client
    if vc is None or not vc.is_connected():
        await ctx.send('არ არის მუსიკა ჩართული')
        return
    if vc.is_paused():
        vc.resume()
    else:
        await ctx.send('არ არის მუსიკა ჩართული')

client.add_command(resume)

@commands.command()
async def pause(ctx):
    vc = ctx.guild.voice_client
    if vc is None or not vc.is_connected():
        await ctx.send('არ არის მუსიკა ჩართული')
        return
    vc.pause()

@commands.command()
async def next(ctx):
    vc = ctx.guild.voice_client
    if vc is None or not vc.is_connected():
        await ctx.send('ბოტი არ არის ჩენელში')
        return
    if not vc.is_playing():
        await ctx.send('არ არის მიმდინარე მუსიკა')
        return
    vc.stop()

client.add_command(next)

client.add_command(pause)

@commands.command()
async def stop(ctx):
    vc = ctx.guild.voice_client
    if vc.is_playing() or vc.is_paused():
        vc.stop()
    else:
        await ctx.send('არ არის მუსიკა ჩართული') 

client.add_command(stop)

@commands.command()
async def leave(ctx):
    vc = ctx.guild.voice_client
    if vc is None or not vc.is_connected():
        await ctx.send('არ არის ბოტი დაკავშირებული')
        return
    if vc.is_playing():
        vc.stop()
    server_id = ctx.guild.id
    if server_id in queues:
        queues.pop(server_id)
    await vc.disconnect()
    await ctx.send('მაგრად')

client.add_command(leave)
TOKEN = 'YOUR TOKEN HERE'
client.run(TOKEN)


