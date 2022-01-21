from discord_slash.utils.manage_components import create_button, create_actionrow, wait_for_component, create_select, create_select_option
from discord_slash.utils.manage_commands import create_option
from discord_slash import SlashCommand, SlashContext
from discord_slash.model import ButtonStyle
from colorama import Fore, Style
from discord.ext import commands
import platform as pf
import random as r
import time as t
import markovify
import discord
import json
import nltk
import os
import re


PREFIX = 'q:'
INV_LINK = 'https://discord.com/api/oauth2/authorize?client_id=931741073397653505&permissions=283467959296&scope=applications.commands%20bot'
GUILD_IDS = [845199962450034728]
RES = Style.RESET_ALL
BOL = Style.BRIGHT
YE = Fore.YELLOW
GR = Fore.GREEN
CY = Fore.CYAN
RE = Fore.RED
DATA = os.path.join( os.path.dirname(__file__) , 'DATA' )
MESSAGES = os.path.join( DATA, 'MESSAGES' )
CONFIG_PATH = os.path.join( os.path.dirname(__file__), 'config.json' )


# If the config file doesnt exists, warns the user
if not os.path.isfile(CONFIG_PATH):
    print(f'{BOL}{RE}ERROR:{RES}{RE} config.json file does not exist{RES}')
    print(f'{BOL}[DEBUG]{RES} Looking for config.json at {CONFIG_PATH}{RES}')
    exit()
# Gets stuff from the config
with open(CONFIG_PATH) as f:    config = json.load(f)
TOKEN = config['token']
PREFIX = config['prefix']
CHANNEL_ID = config['channel']
AI_CHANCE = config['ai_chance']


bot = commands.Bot( command_prefix=PREFIX )
slash = SlashCommand(bot, sync_commands=True)










class POSifiedText(markovify.NewlineText):
	def word_split(self, sentence):
		words = re.split(self.word_split_pattern, sentence)
		words = [ "::".join(tag) for tag in nltk.pos_tag(words) ]
		return words

	def word_join(self, words):
		sentence = " ".join(word.split("::")[0] for word in words)
		return sentence






cls = lambda: os.system('cls') if pf.system() == 'Windows' else os.system('clear')
cls()


def get_msges(user):
    # Gets JSON file path
    json_path = os.path.join( MESSAGES, f'{user.id}.json' )
    # Check if its exist
    if not os.path.exists(json_path):    return {}
    # Reads the file
    with open(json_path) as f:           data = json.load(f)
    # Returns data
    return data



async def make_chc_comp(ctx):
    # Gets all the channels in the guild
    channels = ctx.guild.text_channels
    # Makes the options
    options = [create_select_option(label=f'#{ch} ({ch.id})', value=str(ch.id)) for ch in channels]
    # Makes the select
    select = create_select(options=options, min_values=1, max_values=1)
    # Makes the action row
    actionrow = create_actionrow(select)
    # Returns the component
    return [actionrow]



def save_msg(msg: discord.message):
    # Gets JSON file path
    json_path = os.path.join( MESSAGES, f'{msg.author.id}.json' )
    # Gets the prev data
    data = get_msges(msg.author)
    # Adds all the stuff
    data[str(msg.id)] = {
    'content': msg.content,
    'id': str(msg.id),
    'author': str(msg.author.id),
    'guild': str(msg.guild.id),
    'channel': str(msg.channel.id),
    'jump_url': msg.jump_url,
    'created_at': str(int(msg.created_at.timestamp()))
    }
    # Saves it
    with open(json_path,'w') as f:
        json.dump(data, f, indent=4)



async def reply_randomly(channel):
    messages = {}
    # Goes thro all the files
    for file in os.listdir(MESSAGES):
        # Checks if its cache
        if file.startswith('.'):    continue
        # Gets the json data
        with open(os.path.join(MESSAGES, file)) as f:    data = json.load(f)
        # Goes thro the data
        for key in data:
            messages[key] = data[key]
    # Selects a random key
    key = r.choice(list(messages.keys()))
    # Gets the message
    sel_msg = messages[key]
    msg_cont = sel_msg['content']
    # Says it
    await channel.send(msg_cont)
    # Logging
    print(f'{BOL}{CY}<{bot.user}>{RES}{CY} {msg_cont}{RES}')



async def ai_reply_randomly(message):
    # Gets all the files
    files = os.listdir(MESSAGES)
    # Removes the cache files
    files = [f for f in files if not f.startswith('.')]
    # Selectes a random file
    rand_file = r.choice(files)
    # Extracts the data
    with open(os.path.join(MESSAGES, rand_file)) as f:    data = json.load(f)
    # Gets the content of all the messages
    msgs = [data[key]['content'] for key in data]
    # Converts it to a markov-able string
    text = '\n'.join(msgs)
    # Makes the model
    text_model = POSifiedText(text)
    # Makes a new sentence
    new_sentence = text_model.make_short_sentence(1000)
    # Checks if the new sentence is empty. If it is, sends a normal random message
    if not new_sentence:
        print(f'{BOL}{RE}[FAILED AI] {CY}<{message.author}>{RES}')
        await reply_randomly(message.channel)
        return
    # Sends it
    await message.channel.send(new_sentence)
    # Logging
    print(f'{BOL}{CY}[AI] <{bot.user}>{RES}{CY} {new_sentence}{RES}')



async def quote_func(ctx, user):
    # if the user is none, makes the author the user
    if not user:    user = ctx.author
    # Gets the messages
    msges = get_msges(user)
    # Gets the keys
    keys = list(msges.keys())
    # If there are no keys, tells the user
    if not keys:
        await ctx.reply(f'I am afraid I have no data for {user.mention}')
        return
    # Selects a random key
    key = r.choice(keys)
    # Gets the message
    sel_msg = msges[key]

    # Makes the embed
    embed = discord.Embed(color=0x00ff00, description=sel_msg['content'])
    embed.set_author(name=f'{user.name}#{user.discriminator}', icon_url=user.avatar_url)
    embed.set_footer(text=key)
    # Send the embed
    await ctx.reply(embed=embed)














# Once ready
@bot.event
async def on_ready():
    print(f'{GR}[USING {bot.user} on {t.asctime()}]{RES}\n')







# Ping
@bot.command('ping')
async def ping(ctx):
    await ctx.reply('Pong!')



# Quote
@bot.command('quote', description='Quotes a random message sent by the user')
async def quote_(ctx, user: discord.User=None):
    await quote_func(ctx, user)
@slash.slash(name="quote", description='Quotes a random message sent by the user', options=[create_option(name="user",description="The user you want to get a random message of, by default (ie by leaving it empty) it is the author",option_type=6,required=False)])
async def quote__(ctx: SlashContext, user: discord.Member=None):
    await quote_func(ctx, user)








# Chance
options = create_option(name='chance', description='The bot will send an AI generated message every [chance] number of messages', option_type=4, required=False)
@slash.slash(name='chance', description='The chance of the bot sending an AI generated message', options=[options]) 
async def chance_(ctx:SlashContext, chance:int=None):
    # Checks if author has manage channels permission
    if not ctx.author.guild_permissions.manage_channels:
        # Tells them that they need perms
        await ctx.reply(f'I am sorry but only people who have the `Manage Channels` permissions can use this command', hidden=True)
        return
    global AI_CHANCE, config
    
    # Tells the chance
    if not chance:
        await ctx.reply(f'The bot sends an AI generated message every {AI_CHANCE} messages')
        return
    
    # Sets the chance
    AI_CHANCE = chance
    config['ai_chance'] = str(AI_CHANCE)
    # Saves it
    with open(CONFIG_PATH, 'w') as f:    json.dump(config, f, indent=4)
    # Tells the user its done
    await ctx.reply(f'The bot will now send an AI generated message every {AI_CHANCE} messages')
    






# Config
@slash.slash(name="config", description='Edit the settings of the bot')
async def config_(ctx: SlashContext):
    # Checks if author has manage channels permission
    if not ctx.author.guild_permissions.manage_channels:
        # Tells them that they need perms
        await ctx.reply(f'I am sorry but only people who have the `Manage Channels` permissions can use this command', hidden=True)
        return
    global CHANNEL_ID, config

    chc_actrow = create_actionrow(
        create_button(style=ButtonStyle.blue, label='Channel'),
        create_button(style=ButtonStyle.red, label='Exit')
        )

    embed = discord.Embed(title='Config', description='Configure the bot', color=0x0000ff)
    embed.add_field(name='Channel', value=f'<#{CHANNEL_ID}> ({CHANNEL_ID})', inline=False)
    await ctx.reply(embed=embed, components=[chc_actrow])

    # Checks if the author is clicking the buttons
    while True:
        comp_ctx:ComponentContext = await wait_for_component(bot, components=[chc_actrow])
        if ctx.author.id == comp_ctx.author.id:    break
    # Gets the choice
    chc = comp_ctx.component['label']


    # Channel
    if chc == 'Channel':
        embed = discord.Embed(title='Channel', description=f'Please select the channel where the bot should operate. The current one is <#{CHANNEL_ID}>', color=0x0000ff)
        comp = await make_chc_comp(ctx)
        await comp_ctx.edit_origin(components=comp, embed=embed)
        # Checks if the author is clicking the buttons
        while True:
            comp_ctx:ComponentContext = await wait_for_component(bot, components=comp)
            if ctx.author.id == comp_ctx.author.id:
                break
        # Gets the choice
        allow_chc = comp_ctx.selected_options
        # Enacts on the choice
        CHANNEL_ID = allow_chc[0]
        config['channel'] = CHANNEL_ID
        # Saves the config
        with open(CONFIG_PATH,'w') as f:    json.dump(config, f, indent=4)
        # Tells the user
        embed = discord.Embed(title='Channel', description=f'The channel has been changed to <#{CHANNEL_ID}>', color=0x0000ff)
        await comp_ctx.edit_origin(embed=embed, components=[])
    

    # Exit
    if chc == 'Exit':
        await comp_ctx.edit_origin(components=[])













# When someone messages smth
@bot.listen('on_message')
async def on_message(msg):
    author = msg.author
    content = msg.content

    # Checks if the message was sent in the designated channel
    if str(msg.channel.id) != CHANNEL_ID:
        return
    # Checks if I sent the message
    if author.id == bot.user.id:    return
    # Checks if the author is a bot
    if author.bot:
        print(f'{YE}{author} is a bot{RES}')
        return
    # Checks if the message is empty
    if not len(content):
        print(f'{YE}{author} sent an empty message{RES}')
        return
    # Checks if the msg contains any of the common bot prefixes
    if content.startswith( ('!','$','.','/','\\',PREFIX) ):
        print(f'{YE}{author} probably used a bot command ({content}){RES}')
        return

    print(f'{BOL}<{author}>{RES} {content}')
    save_msg(msg)

    # Sends an AI generated msg every [chance] messages
    if r.randint(1, int(AI_CHANCE)) == 1:       await ai_reply_randomly(msg)
    else:                                       await reply_randomly(msg.channel)









# When someone deletes a message
@bot.listen('on_message_delete')
async def on_message_delete(message):
    # Logging
    print(f'{BOL}{RE}<{message.author}>{RES}{RE} {message.content}{RES}')
    # Checks if we have the author in the database
    json_path = os.path.join(MESSAGES, f'{message.author.id}.json')
    if not os.path.exists(json_path):    return
    # Checks if we have the message in the database
    with open(json_path, 'r') as f:    msges = json.load(f)
    if str(message.id) not in msges:    return
    # Removes the message from the database
    del msges[str(message.id)]
    with open(json_path, 'w') as f:    json.dump(msges, f, indent=4)
    















# Makes the DATA and MESSAGES folders if they dont exist
os.makedirs(DATA, exist_ok=True)
os.makedirs(MESSAGES, exist_ok=True)




bot.run(TOKEN)


