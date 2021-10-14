import discord
import os
import requests
import json
import re
from replit import db
from server import keep_alive
#import asyncio
client = discord.Client()
token = os.environ['TOKEN']

# Set the default prefix to be '\'
DEFAULT_PREFIX = '$'
def get_prefix(bot_obj, message) -> str:
    # a custom prefix can be retrieved with the guild's ID
    try:
        with open("prefixes.json", 'r') as f:
            prefixes = json.load(f)

        return prefixes[str(message.guild.id)]

    except AttributeError:  # triggered when command is invoked in dms
        return DEFAULT_PREFIX

    except KeyError:  # triggered when the server prefix has never been changed
        return DEFAULT_PREFIX

client = commands.Bot(command_prefix=get_prefix, intents=intents)


@client.event
async def on_guild_remove(guild):
    try:
        with open("prefixes.json", 'r') as f:
            prefixes = json.load(f)

        prefixes.pop(str(guild.id))

        with open("prefixes.json", 'w') as f:
            json.dump(prefixes, f, indent=2)
    except KeyError:  # the server never changed the default prefix
        pass

@client.command(aliases=["PREFIX", "Prefix", "pREFIX"])
@has_permissions(administrator=True)
async def prefix(ctx, new_prefix: str):

    if ctx.guild is None:
        await ctx.reply("**You cannot change the prefix outside of a server!**")
        return

    with open("prefixes.json", 'r') as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = new_prefix

    with open("prefixes.json", 'w') as f:
        json.dump(prefixes, f, indent=2)

    await ctx.send(f"**Prefix changed to {new_prefix}**")

@prefix.error
async def prefix_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply("**Incorrect usage!\n"
                        f"Example: {get_prefix(client, ctx)}prefix .**")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.reply("**You do not have the permission to change the server prefix!**")


def get_weather(query):
    api_key = os.environ['api_key']
    response = requests.get("http://api.weatherapi.com/v1/current.json?key=" +
                            str(api_key) + "&q=" + query + "&aqi=no")
    dict_obj = json.loads(response.text)
    try:
      location = dict_obj["location"]
      current = dict_obj["current"]
      condition = current["condition"]
      resp = "Location : " + location["name"] + "\n" + "Country : " + location[
          "country"] + "\n"+"Region : "+location["region"]+"\n" + "Last Updated : " + current[
              "last_updated"] + "\n" + "Temperature in °C : " + str(
                  current["temp_c"]) + "\n" + "Climate : " + condition["text"]
    except Exception as e:
      resp="Location not found \n try co-ordinates method-$weather <latitude>,<longitude>"
    return resp


@client.event
async def on_ready():
    print("We have logged in as  {0.user}".format(client))


@client.event
async def on_message(message):
    author=message.author
    author_str=str(author)
    if author == client.user:
        return
    msg = message.content
    if msg.startswith("$hello"):
        await message.channel.send("Hello! {} .\n * To know more about the bot type $help".format(author))
    elif msg.startswith("$help"):
      with open("DiscordCmdDoc.txt","r") as file:
        await message.channel.send(file.read())

    elif msg.startswith("$weather"):
        k=re.match("^\$weather\s*(#?(([a-zA-Z\s\d]+)|([\d\.]+\s*\,\s*[\d\.]+)))$",msg)
        value=k.group(1)
        if (k):
          if (value.startswith("#")):
            if author_str in db.keys() and value[1:] in db[author_str].keys():
              await message.channel.send(get_weather(db[author_str][value[1:]]))
            else:
              await message.channel.send("The tag hasn't been defined")
          else:
            await message.channel.send(get_weather(value))
        else:
          await message.channel.send("Something went wrong")
    elif msg.startswith("$save_tags"):
      k=re.match("^\$save_tags\s+(\w+)\s+(([a-zA-Z\s]+)|([\d\.]+\,[\d\.]+))$",msg)
      if k:
        if author_str in db.keys():
          #print("I am here")
          user_db=db[author_str]
          user_db[k.group(1)]=k.group(2)
          db[author_str]=user_db
          await message.channel.send("The tag has been saved successfully")
        else:
          db[author_str]={k.group(1):k.group(2)}
          print("Space for the user and the data has been created and updated successfully")
      else:
        await message.channel.send("Invalid Tags")
        #if((k=re.match("^\$weather\s*(name)",msg)):
        #  print("Hello World")
keep_alive()
client.run(token)
#$weather $save myhome <co-ordinates>
#$weather #myhome
