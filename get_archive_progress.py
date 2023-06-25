from datetime import datetime, timezone
from json import load
from os import path, makedirs
from mvm_main import net_request

if not path.isfile('./archive-progress-players.json'):
    print("Could not find 'archive-progress-players.json'. Generating example file...")
    fileContent = "[{\n	\"steamid\": \"76561197980854307\",\n	\"personaname\": \"Raivop\"\n},\n{\n	\"steamid\": \"76561198055787630\",\n	\"personaname\": \"1948°F\"\n},\n{\n	\"steamid\": \"76561198029695777\",\n	\"personaname\": \"Pum\"\n},\n{\n	\"steamid\": \"76561198149323183\",\n	\"personaname\": \"Ezo\"\n},\n{\n	\"steamid\": \"76561198020822150\",\n	\"personaname\": \"MON@H\"\n},\n{\n	\"steamid\": \"76561198151903732\",\n	\"personaname\": \"olle\"\n},\n{\n	\"steamid\": \"76561198202920644\",\n	\"personaname\": \"Spirit\"\n},\n{\n	\"steamid\": \"76561197977522475\",\n	\"personaname\": \"m00\"\n},\n{\n	\"steamid\": \"76561197981808097\",\n	\"personaname\": \"Spelworm\"\n},\n{\n	\"steamid\": \"76561198041913192\",\n	\"personaname\": \"Smoke\"\n},\n{\n	\"steamid\": \"76561198055313095\",\n	\"personaname\": \"fellen\"\n},\n{\n	\"steamid\": \"76561197970303115\",\n	\"personaname\": \"xPert\"\n},\n{\n	\"steamid\": \"76561198077120499\",\n	\"personaname\": \"bubo2000\"\n}]\n"
    with open('./archive-progress-players.json', mode='wt', encoding='utf-8') as outputFile:
        outputFile.write(fileContent)
with open('archive-progress-players.json') as f:
    players = load(f)
get_start_time = datetime.now(timezone.utc)
fileSaveName = "archiveprogress-" + get_start_time.date().strftime('%Y_%m_%d') + "-" + get_start_time.time().strftime('%H%M%SUTC') + ".txt"

writingList = []
longestName = len(max([i['personaname'] for i in players], key=len)) + 2

print("Retrieving mission information...")
missionCount = len(net_request('https://archive.potato.tf/api/missioninfo','json'))

# todo: net request rate limit
for player in players:
    print("Getting completion information for '" + player["personaname"] + "'...")
    currentPlayer = net_request('https://archive.potato.tf/api/waveprogress?steamid=' + player["steamid"],'json')
    currentName = (player["personaname"] + ":\t").expandtabs(longestName)
    writingList.append([currentName + str(currentPlayer["completedMissions"]) + "/" + str(missionCount) + "\nhttps://archive.potato.tf/progress/" + player["steamid"],currentPlayer["completedMissions"]])

# sort alphabetically, then by completion
writingList.sort(key=lambda x: str(x[0].lower()))
writingList.sort(key=lambda x: int(x[1]), reverse=True)
# strip tuple to list
writingList = [i[0] for i in writingList]

writingList.append("\nAll Speedruns:\nhttps://gist.github.com/mtxfellen/cd64e622942676a76a778c99f63b8a81")

# SAVE RESULT
if not path.exists('./output/'):
    makedirs('./output/')
with open('./output/' + fileSaveName, mode='wt', encoding='utf-8') as outputFile:
    outputFile.write('\n'.join(writingList) + '\n')
print("Archive progress saved to \"" + path.abspath('./output/' + fileSaveName) + "\".")
