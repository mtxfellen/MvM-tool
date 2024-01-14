from time import sleep
import mvm_main as mvm
from datetime import datetime, timezone, timedelta
from os import path, makedirs
from collections import Counter
from requests import patch # pip install requests
from json import dumps, load

# == BEGIN ==

print("\nPotato.tf Speedruns Script by fellen.\n https://github.com/mtxfellen/MvM-tool\n")

# LOOK FOR ACTIVE CAMPAIGN
selected_tour_url = 'https://potato.tf/'
print("Looking for active campaign from " + selected_tour_url + "...")
activeTours = mvm.get_active_tours(selected_tour_url) # perhaps there's an api request to do this properly
selected_tour = activeTours[0]

# ALLOW SWAP TO ARCHIVE IF ACTIVE FOUND
# todo: add automatic discovery method for beta tests
# todo: allow custom URL input; functions to do this are already implemented in mvm_main.py
if len(activeTours) == 2:
    printNow = "Detected active Operation " + activeTours[0] + ". Switch to " + activeTours[1] + " instead? [Y/n]"
    print(printNow)
    switchChoice = mvm.loop_input(['yes','y','ye','no','n'],1)
    if switchChoice <= 2:
        printNow = "Switching to " + activeTours[1] + " missions..."
        print(printNow)
        selected_tour_url = 'https://archive.potato.tf/'
        selected_tour = activeTours[1]
    else:
        printNow = "Getting missions for Operation " + activeTours[0] + "..."
        print(printNow)

# GET MISSION AND MAPS
# stored as list of dicts
print("Getting missions for " + selected_tour + "...")
timeStart = datetime.now().timestamp()
map_list = mvm.fix_oxidize(mvm.net_request(selected_tour_url + "api/mapinfo",'json'))
mission_list = mvm.net_request(selected_tour_url + "api/missioninfo",'json')

# GENERATE FILE NAME AND HEADER
get_start_time = datetime.now(timezone.utc)
fileSaveName = "allruns-" + get_start_time.date().strftime('%Y_%m_%d') + "-" + get_start_time.time().strftime('%H%M%SUTC') + ".txt"
if selected_tour == 'Potato Archive': 
    fileHeader = "All " + selected_tour + " Speedruns, Last Updated: " + get_start_time.date().strftime('%d/%m/%Y ') + get_start_time.time().strftime('%H:%M UTC')
else:
    fileHeader = "All Operation " + selected_tour + " Speedruns, Last Updated: " + get_start_time.date().strftime('%d/%m/%Y ') + get_start_time.time().strftime('%H:%M UTC')
writingList = [fileHeader]
firstPlaceRunners = []
firstPlaceRuns = []
sleep(max(0,1.2 - (datetime.now().timestamp() - timeStart)))

# ITERATE THROUGH MAPS
for i in range(len(map_list)):
    print("Getting times for " + map_list[i]["niceMapName"] + "...")
    timeStart = datetime.now().timestamp()
    workingMap_Speedrun = mvm.net_request(selected_tour_url + 'api/speedrun?map=' + map_list[i]["name"],'json')
    workingMap_Missions = sorted(set(j["mission"] for j in workingMap_Speedrun))
    if len(workingMap_Missions) == 1:
        writingList.append(map_list[i]["niceMapName"] + " (" + str(len(workingMap_Missions)) + " mission)")
    else:  
        writingList.append(map_list[i]["niceMapName"] + " (" + str(len(workingMap_Missions)) + " missions)")
    
    # CREATE LIST OF LISTS OF DICTS OF SPEEDRUNS
    workingMap_SpeedrunSplit = [[] for j in range(len(workingMap_Missions))]
    for j in range(len(workingMap_Speedrun)):
        for k in range(len(workingMap_Missions)):
            if workingMap_Missions[k] == workingMap_Speedrun[j]["mission"]:
                workingMap_SpeedrunSplit[k].append(workingMap_Speedrun[j])

    # ITERATE THROUGH MISSIONS ON MAP
    for j in range(len(workingMap_Missions)):
        # todo: review; i'm pretty sure this isn't necessary but i was too occupied with getting
        # a functional program first to simplify it at the time
        lastRun = 0
        for k in range(lastRun,len(mission_list)):
            if workingMap_Missions[j] == mission_list[k]["mission"]:
                lastRun = k
                break
        workingMission_InfoString = "    " + mission_list[lastRun]["missionNiceName"] + " - " + mvm.num_2_difficulty(mission_list[lastRun]["difficulty"]) + " (Operation " + mission_list[lastRun]["campaignName"] + ", "
        if mission_list[lastRun]["waveCount"] == 1:
            workingMission_InfoString += "1 wave)"
        else:
            workingMission_InfoString += str(mission_list[lastRun]["waveCount"]) + " waves)"
        writingList.append(workingMission_InfoString)
        firstPlaceRuns.append(workingMap_SpeedrunSplit[j][0])
        # check if there are at least 3 entries and iterate through whichever is smaller
        entryDisplays = 3
        # todo: at a glance this looks like it might not do whatever i originally intended it to do
        if len(workingMap_SpeedrunSplit[j]) < entryDisplays:
            entryDisplays = len(workingMap_SpeedrunSplit[j])
        elif entryDisplays == 0:
            writingList.append("      No entries.")
        else:
            # check if hours in any runs, chop leading 0 otherwise
            # todo: see mvm_main.py
            for k in range(entryDisplays):
                currentRunLine = "      " + str(timedelta(seconds=int(workingMap_SpeedrunSplit[j][k]["time"])))[2:] + " | " + datetime.fromtimestamp(workingMap_SpeedrunSplit[j][k]["timeAdded"], tz=timezone.utc).strftime('%d/%m/%Y') + " | "
                playersCurrentRunLine = ""
                for l in range(len(workingMap_SpeedrunSplit[j][k]["players"])):
                    if k == 0:
                        firstPlaceRunners.append(str(workingMap_SpeedrunSplit[j][k]["players"][l]["personaname"]))
                    playersCurrentRunLine = playersCurrentRunLine + mvm.shorten_string(str(workingMap_SpeedrunSplit[j][k]["players"][l]["personaname"]), 20) + ", "
                if l > 5 and mission_list[lastRun]["mission"] != 'adv_dover_2':
                    currentRunLine = currentRunLine + "(BUGGED) " + playersCurrentRunLine
                else:
                    currentRunLine = currentRunLine + playersCurrentRunLine
                currentRunLine = mvm.rem_bidir(currentRunLine)
                writingList.append(currentRunLine[:-2])
        writingList.append("")
    # adhere to a rough request limit of 100/min
    sleep(max(0,0.6 - (datetime.now().timestamp() - timeStart)))

# append map stats
writingList.append("== Stats ==\n\nMaps: " + str(len(map_list)) + "\nMissions: " + str(len(mission_list)) + "\n")

# append recents stats
min_recent_runs = 10 # controls the target number of recent runs to list
target_age = 302400 # controls the target age of runs to list (will override the recent runs)
if len(firstPlaceRuns) > min_recent_runs:   # should be compared recent runs rather than all first places(?)
    oldest_allowed = get_start_time.timestamp() - target_age
    writingList.append("Most recent #1 runs:")
    firstPlaceRuns = sorted(firstPlaceRuns,key=lambda x: int(x['timeAdded']),reverse=True)
    if firstPlaceRuns[(min_recent_runs)]['timeAdded'] > oldest_allowed:
        for i,currentRun in enumerate(firstPlaceRuns):
            if i == 10 or currentRun['timeAdded'] < oldest_allowed :
                break
        firstPlaceRuns = firstPlaceRuns[0:i]
    else:
        firstPlaceRuns = firstPlaceRuns[0:(min_recent_runs)]
    for currentRun in firstPlaceRuns:
        writingList.append('  ' + currentRun['mapNiceName'] + ' - ' + currentRun['missionNiceName'] + ' in ' + str(timedelta(seconds=int(currentRun['time'])))[2:] + ' dated ' + datetime.fromtimestamp(currentRun['timeAdded'], tz=timezone.utc).strftime('%H:%M, %d/%m/%Y'))
        playersCurrentRunLine = ''
        for player in currentRun['players']:
            playersCurrentRunLine = playersCurrentRunLine + mvm.shorten_string(str(player['personaname']), 20) + ", "
        writingList.append('    ' + mvm.rem_bidir(playersCurrentRunLine[:-2]))
        
# append top stats
iterLength = 20 # controls the target number of top runners to list
if len(firstPlaceRunners) < iterLength:
    iterLength = len(firstPlaceRunners)
firstPlaceRunners = Counter(firstPlaceRunners).most_common(iterLength)
writingList.append("\nTop " + str(iterLength) + " runners (by most #1s):")
for i in range(iterLength):
    writingList.append("  " + str(firstPlaceRunners[i][0]) + ": " + str(firstPlaceRunners[i][1]))

writingList.append("") # end on a newline

# SAVE RESULT
if not path.exists('./output/'):
    makedirs('./output/')
fileContent = '\n'.join(writingList)
with open('./output/' + fileSaveName, mode='wt', encoding='utf-8', newline='\n') as outputFile:
    outputFile.write(fileContent)
print("All speedruns saved to \"" + path.abspath('./output/' + fileSaveName) + "\".")

# IMPORT GITHUB API SETTINGS
if path.isfile('./github-access.json'):
    with open('github-access.json') as github_access:
        github_settings = load(github_access)
    github_token = str(github_settings['github_token'])
    gist_id = str(github_settings['gist_id'])
    upload_name = str(github_settings['upload_name'])
    
    # UPLOAD GIST TO GITHUB
    # todo: deal properly with response codes (see: https://do-cs.github.com/en/rest/gists/gists?apiVersion=2022-11-28#update-a-gist)
    if github_token != 'GITHUB_TOKEN' and gist_id != 'GIST_ID':
        print("Revising Github gist...")
        github_headers = {'Authorization': 'Bearer ' + github_token,'Accept':'application/vnd.github+json'}
        patch('https://api.github.com/gists/' + gist_id, data=dumps({'files':{upload_name:{"content":fileContent}}}),headers=github_headers)
else:
    print("Could not find 'github-access.json'. Generating example file...")
    fileContent = "{\n	\"github_token\": \"GITHUB_TOKEN\",\n	\"gist_id\": \"GIST_ID\",\n	\"upload_name\": \"all-speedruns.txt\"\n}\n"
    with open('./github-access.json', mode='wt', encoding='utf-8', newline='\n') as outputFile:
        outputFile.write(fileContent)

# == END ==
