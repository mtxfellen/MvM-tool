from datetime import datetime, timezone
from json import load
from os import path, makedirs
from mvm_main import net_request

with open('archive-progress-players.json') as f:
    players = load(f)
get_start_time = datetime.now(timezone.utc)
fileSaveName = "archiveprogress-" + get_start_time.date().strftime('%Y_%m_%d') + "-" + get_start_time.time().strftime('%H%M%SUTC') + ".txt"
print("Retrieving mission information...")
missionCount = len(net_request('https://archive.potato.tf/api/missioninfo','json'))

writingList = []
# todo: align strings with tabs
# todo: net request rate limit
for player in players:
    print("Getting completion information for '" + player["personaname"] + "'...")
    currentPlayer = net_request('https://archive.potato.tf/api/waveprogress?steamid=' + player["steamid"],'json')
    writingList.append([player["personaname"] + ": \t" + str(currentPlayer["completedMissions"]) + "/" + str(missionCount) + "\nhttps://archive.potato.tf/progress/" + player["steamid"],currentPlayer["completedMissions"]])
writingList = sorted(writingList,key=lambda x:(str(x[0]),int(x[1])),reverse=True)
writingList = [i[0] for i in writingList]

# SAVE RESULT
if not path.exists('./output/'):
    makedirs('./output/')
with open('./output/' + fileSaveName, mode='wt', encoding='utf-8') as outputFile:
    outputFile.write('\n'.join(writingList) + '\n')
print("Archive progress saved to \"" + path.abspath('./output/' + fileSaveName) + "\".")
