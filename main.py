import discord
from discord.ext import commands
import os
import requests
import time
import json
from datetime import datetime
import pytz
from keep_alive import keep_alive

# Token des Bots
TOKEN = os.environ['TOKEN']

# Intents erstellen
intents = discord.Intents.default()
intents.typing = False
intents.presences = False

# Client erstellen
bot = commands.Bot(command_prefix='!', intents=intents)


async def SendMessage(channel_id, Message):
  channel = bot.get_channel(channel_id)

  if channel:
    await channel.send(Message)


def create_games_folder():
  folder_name = "Games"
  if not os.path.exists(folder_name):
    os.makedirs(folder_name)
    return True


def create_file_in_games_folder(file_name, content=""):
  file_path = os.path.join("Games", file_name)
  with open(file_path, "w") as file:
    file.write(content)
  return True


def edit_file_in_games_folder(file_name, new_content):
  file_path = os.path.join("Games", file_name)
  if os.path.exists(file_path):  # Korrekte Verwendung von os.path.exists
    with open(file_path, "w") as file:
      file.write(new_content)
    return True
  else:
    return False


def delete_file_in_games_folder(file_name):
  file_path = os.path.join("Games", file_name)
  if os.path.exists(file_path):
    os.remove(file_path)
    return True
  else:
    return False


def read_file_in_games_folder(file_name):
  file_path = os.path.join("Games", file_name)
  if os.path.exists(file_path):
    with open(file_path, "r") as file:
      content = file.read()
    return content
  else:
    return False


async def GetGameFromGroup(GroupID, PlaceID):
  MadCityURL = f"https://games.roblox.com/v2/groups/{GroupID}/gamesV2?accessFilter=2&limit=100&sortOrder=Asc"

  MadCityResponse = requests.get(MadCityURL)

  if MadCityResponse.status_code == 200:
    data = json.loads(MadCityResponse.text)

    if "data" in data:
      games = data["data"]
      if games and len(games) > 0:
        first_game = games[0]
        if "rootPlace" in first_game:
          root_place_info = first_game["rootPlace"]
          if "id" in root_place_info:
            root_place_id = root_place_info["id"]
            if int(root_place_id) == int(PlaceID):
              if "name" in first_game:
                Game_name = first_game["name"]
              if "updated" in first_game:
                updated = first_game["updated"]
                # Remove milliseconds and 'Z' from the ISO format
                updated = updated.split(".")[0]
                updated = updated.rstrip('Z')
                timestamp = datetime.fromisoformat(updated)
                eastern = pytz.timezone('US/Eastern')
                timestamp_eastern = timestamp.replace(
                    tzinfo=pytz.UTC).astimezone(eastern)
                formatted_time = timestamp_eastern.strftime(
                    "%Y-%m-%d %H:%M:%S %Z")
                if read_file_in_games_folder(
                    str(GroupID) + "_" + str(PlaceID)) == formatted_time:
                  print("No Update!", Game_name)
                  await SendMessage(1221145193181483038,
                                    f"No Update Detected! for {Game_name}\n")
                else:
                  print("Update Detected!")
                  await SendMessage(
                      1221145193181483038,
                      f"Update Detected for {Game_name}\n||https://www.roblox.com/games/{PlaceID}|| \n -> <@&1188447404538744842>"
                  )
                  if edit_file_in_games_folder(
                      str(GroupID) + "_" + str(PlaceID),
                      formatted_time) == False:
                    create_file_in_games_folder(
                        str(GroupID) + "_" + str(PlaceID), formatted_time)
                return formatted_time
  else:
    print("Roblox API error! PlaceID:", PlaceID)
    time.sleep(10)


@bot.event
async def on_ready():
  print(f'Eingeloggt als {bot.user}')
  keep_alive()
  create_games_folder()
  while True:
    # GetGameFromGroup(GroupID, PlaceID)
    await GetGameFromGroup(3642592, 1224212277)  # Mad City
    await GetGameFromGroup(5774246, 4872321990)  # Islands
    await GetGameFromGroup(4698921, 2788229376)  # Da Hood
    time.sleep(2)
    await GetGameFromGroup(4328109, 2534724415)  # Emergency Response
    await GetGameFromGroup(8505490, 185655149)  # Bloxburg
    await GetGameFromGroup(3059674, 606849621)  # Jailbreak
    # time.sleep(2)

    time.sleep(10)


# Den Bot mit dem Token starten
bot.run(TOKEN)
