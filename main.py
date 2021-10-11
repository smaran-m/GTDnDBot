# TODO:
# Check for previous database entries to overwrite character
# Fix log command, user being converted to bool somewhere?
# Fix commands that take user inputs
# Add deletechar command, taking user input
# Host bot in cloud
# Formatted character outputs with embedded token?

import os
import discord
import asyncio
from replit import db
from discord.ext import commands

token = os.environ['token']
prefix = 'plp '
client = commands.Bot(command_prefix=prefix)

async def confirm_helper(ctx):
  def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == '👍'
  try:
    reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
  except asyncio.TimeoutError:
    await ctx.send('Request timed out.')
    return False
  else:
    return True


@client.event
async def on_ready():
  print("Logged in as {0.user}".format(client)) 

@client.command()
async def newchar(ctx, char_name, char_race, char_class):
  user = ctx.author
  if str(user.id) in db.keys():
    #print(db[str(user.id)])
    await ctx.send('Overwrite your dedicated character?\n> {}\nTo confirm, react with 👍'.format(db[str(user.id)][0].title()))
    if await confirm_helper(ctx):
      db[str(user.id)] = [char_name.lower(), char_race.lower(), char_class.lower(), 1, 0]
      await ctx.send("Created new character\n> {}, Level 1 {} {}".format(char_name.title(), char_race.capitalize(), char_class.capitalize()))
    else:
      await ctx.send("Character creation unsuccessful.")
  else:
    message = 'Create new dedicated character?\n>  {}, Level 1 {} {}\nTo confirm, react with 👍'.format(char_name.title(), char_race.capitalize(), char_class.capitalize())
    await ctx.send(message)
    if await confirm_helper(ctx):
      db[str(user.id)] = [char_name.lower(), char_race.lower(), char_class.lower(), 1, 0]
      await ctx.send("Created new character\n> {}, Level 1 {} {}".format(char_name.title(), char_race.capitalize(), char_class.capitalize()))
    else:
      await ctx.send("Character creation unsuccessful.")

@client.command()
async def character(ctx, user: discord.Member = None):
    user = user or ctx.author
    if user != None and str(user.id) in db.keys():
      char = db[str(user.id)]
      await ctx.send("{} plays:\n> {}, Level {} {} {}".format(user.id, char[0].title(), char[3], char[1].capitalize(), char[2].capitalize()))
    else:
      await ctx.send("No character found!")

@client.command()
async def delchar(ctx):
  user = ctx.author
  if str(user.id) in db.keys():
    char = db[str(user.id)]
    await ctx.send("Delete character?\n> {}, Level {} {} {}\n**This action cannot be undone**\nTo confirm, react with 👍".format(char[0].title(), char[3], char[1].capitalize(), char[2].capitalize()))
    if await confirm_helper(ctx):
      del db[str(user.id)]
      await ctx.send("Your character has been deleted.")
  else:
    await ctx.send("No character found!")


@client.command()
async def rename(ctx, char_name):
  if str(ctx.author.id) in db.keys():
    old_name = db[str(ctx.author.id)][0]
    db[str(ctx.author.id)][0] = char_name
    await ctx.send("Changed character name.\n>>> Previous: {}\nNew: {}".format(old_name.title(),char_name.title()))
  else:
    await ctx.send("You do not have any characters.")

@client.command()
@commands.has_permissions(administrator = True)
async def changerace(ctx, char_race, user: discord.Member = None):
  user = user or ctx.author
  if user != None and str(user.id) in db.keys():
    char = db[str(user.id)]
    await ctx.send("Change {}'s race?\nTo confirm, react with 👍".format(char[0].title()))
    if await confirm_helper(ctx):
      old_race = char[1]
      char[1] = char_race
      await ctx.send("Changed character race.\n>>> Previous: {}\nNew: {}".format(old_race.title(),char_race.title()))
  else:
    await ctx.send("No character found!")

@client.command()
@commands.has_permissions(administrator = True)
async def changeclass(ctx, char_class, user: discord.Member = None):
  user = user or ctx.author
  if user != None and str(user.id) in db.keys():
    char = db[str(user.id)]
    await ctx.send("Change {}'s class?\nTo confirm, react with 👍".format(char[0].title()))
    if await confirm_helper(ctx):
      old_class = char[2]
      char[2] = char_class
      await ctx.send("Changed character class.\n>>> Previous: {}\nNew: {}".format(old_class.title(),char_class.title()))
  else:
    await ctx.send("No character found!")

@client.command()
@commands.has_permissions(administrator = True)
async def changelevel(ctx, char_level : int, user: discord.Member = None):
  user = user or ctx.author
  if user != None and str(user.id) in db.keys():
    char = db[str(user.id)]
    await ctx.send("Change {}'s level?\nTo confirm, react with 👍".format(char[0].title()))
    if await confirm_helper(ctx):
      old_level = char[3]
      char[3] = char_level

      if char[3] == 1:
        char[4] = 0
      elif char[3] == 2:
        char[4] = 1
      elif char[3] == 3:
        char[4] = 3
      elif char[3] == 4:
        char[4] = 6
      else:
        char[4] = 10 + (char[3] - 4)*4

      await ctx.send("Changed character level.\n>>> Previous: {}\nNew: {}".format(old_level, char_level))
  else:
    await ctx.send("No character found!")

@client.command()
async def dm(ctx):
  user = ctx.author
  member = discord.utils.find(lambda r: r.name == 'Member', ctx.message.guild.roles)
  dmr = discord.utils.find(lambda r: r.name == 'DM', ctx.message.guild.roles)
  vsdm = discord.utils.find(lambda r: r.name == 'VS-DM', ctx.message.guild.roles)

  if (vsdm in user.roles):
    await user.remove_roles(vsdm)
    await ctx.send("Removed VS-DM role.")
  elif (member in user.roles and dmr in user.roles):
    await user.add_roles(vsdm)
    await ctx.send("Added VS-DM role. Welcome to Sakar.")
  else:
    await ctx.send("Member does not meet the requirements (must have Member and DM roles).")

#test this
@client.command()
async def log(ctx, questname, sessions, *users: discord.Member):
  await ctx.send("Log quest?\n> *{}*, lasted {} session(s).\nTo confirm, react with 👍".format(questname, sessions)) #THIS DOES NOT WORK, AUTHOR IS STR OBJECT
  if await confirm_helper(ctx):
    log = client.get_channel(897003243098488882)
    logmsg = "Quest complete!\n> *{}*, lasted {} session(s).\n> Run by {}\n> Adventurers:\n".format(questname.capitalize(), sessions, ctx.author.mention)
    for user in users:
      if str(user.id) in db.keys():
        char = db[str(user.id)]
        oldlvl = char[3]
        char[4] += int(sessions)
        sessionNum = char[4]
        if sessionNum < 1:
          char[3] = 1
        elif sessionNum >= 1 and sessionNum <= 3:
          char[3] = 2
        elif sessionNum > 3 and sessionNum <= 6:
          char[3] = 3
        elif sessionNum > 6 and sessionNum < 10:
          char[3] = 4
        else:
          char[3] = ((sessionNum-10)//4)+5

        logmsg += "> • {} (played by {})\n".format(char[0].title(), user.mention)

        if char[3] > oldlvl:
          await ctx.send("> {} has levelled up!\n> New level: {}".format(char[0].capitalize(), char[3]))
      else:
        logmsg += "> • {}'s character\n".format(user.mention)
        await ctx.send("{} does not have a dedicated character!".format(user.mention))
    await log.send(logmsg)
  else:
      await ctx.send("Game logging unsuccessful.")

# WORK IN PROGRESS COMMANDS
@client.command()
async def newloc(ctx):
  pass

@client.command()
async def leaderboard(ctx):
  charlist = []
  message = '**Leaderboard:\n**'
  for key in db.keys():
    charlist.append(db[key])
  charlist.sort(key = lambda x: x[3], reverse = True)
  #print(charlist)
  rank = 1
  for char in charlist:
    message += ('{}. {}, Level {} {} {}\n'.format(rank, char[0].title(), char[3], char[1].capitalize(), char[2].capitalize()))
    rank += 1
  await ctx.send(message)

@client.command()
@commands.has_permissions(administrator = True)
async def cleardb(ctx):
  await ctx.send("Clear database? **This action cannot be undone.**")
  for key in db.keys():
    del db[key]

#@client.command()
#async def helpme(ctx):
#  comms = ["newchar", "rename", "log", "info", "helpme"]
#  message = 'Commands:'
#  for i in comms:
#    message.add("\n- "+i)
#  await ctx.send(message)

@client.command()
async def info(ctx):
  await ctx.send("GTD&D Polyptech Bot. Contact <@126885302185885697> for any feedback/concerns!\nFor list of commands, use {}help".format(prefix))

client.run(token)