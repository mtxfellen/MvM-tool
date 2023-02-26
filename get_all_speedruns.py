from time import sleep
import mvm_main as mvm
from datetime import datetime, timezone, timedelta
from os import path, makedirs
from collections import Counter

# == BEGIN ==
# LOOK FOR ACTIVE CAMPAIGN
print("Accessing https://potato.tf/...")
selected_tour_url = 'https://potato.tf/'
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
map_list = mvm.net_request(selected_tour_url + "api/mapinfo",'json')
mission_list = mvm.net_request(selected_tour_url + "api/missioninfo",'json')

# DIFFERENTIATE OXIDIZE VERSIONS
# iterates through list backwards (o is closer to z) and continues if both versions have been corrected
twoReplacements = 0
for i in range(len(map_list)-1,0,-1):
    if map_list[i]["fullName"] == 'mvm_oxidize_rr18':
        map_list[i]["niceMapName"] = 'Oxidize RR18'
        twoReplacements += 1
    elif map_list[i]["fullName"] == 'mvm_oxidize_rc3':
        map_list[i]["niceMapName"] = 'Oxidize RC3'
        twoReplacements += 1
    if twoReplacements == 2:
        break
del twoReplacements

# GENERATE FILE NAME AND HEADER
get_start_time = datetime.now(timezone.utc)
fileSaveName = "allruns-" + get_start_time.date().strftime('%Y_%m_%d') + "-" + get_start_time.time().strftime('%H%M%SUTC') + ".txt"
if selected_tour == 'Potato Archive': 
    fileHeader = "All " + selected_tour + " Speedruns, Last Updated: " + get_start_time.date().strftime('%d/%m/%Y ') + get_start_time.time().strftime('%H:%M UTC')
else:
    fileHeader = "All Operation " + selected_tour + " Speedruns, Last Updated: " + get_start_time.date().strftime('%d/%m/%Y ') + get_start_time.time().strftime('%H:%M UTC')
writingList = [fileHeader]
firstPlaceRunners = []

# ITERATE THROUGH MAPS
# todo: add delay for api rate limit, assuming 100 req/min for now
for i in range(len(map_list)):
    print("Getting times for " + map_list[i]["niceMapName"] + "...")
    workingMap_Speedrun = mvm.net_request(selected_tour_url + 'api/speedrun?map=' + map_list[i]["name"],'json')
    workingMap_Missions = sorted(set(j["mission"] for j in workingMap_Speedrun))
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
        # a functional program first to go back and simplify it
        lastRun = 0
        for k in range(lastRun,len(mission_list)):
            if workingMap_Missions[j] == mission_list[k]["mission"]:
                lastRun = k
                break
        workingMission_InfoString = "\t" + mission_list[lastRun]["missionNiceName"] + " - " + mvm.num_2_difficulty(mission_list[lastRun]["difficulty"]) + " (Operation " + mission_list[lastRun]["campaignName"] + ", "
        if mission_list[lastRun]["waveCount"] == 1:
            workingMission_InfoString += "1 wave)"
        else:
            workingMission_InfoString += str(mission_list[lastRun]["waveCount"]) + " waves)"
        writingList.append(workingMission_InfoString)
        # check if there are at least 3 entries and iterate through whichever is smaller
        entryDisplays = 3
        if len(workingMap_SpeedrunSplit[j]) < entryDisplays:
            entryDisplays = len(workingMap_SpeedrunSplit[j])
        elif entryDisplays == 0:
            writingList.append("\t  No entries.")
        else:
            # check if hours in any runs, chop leading 0 otherwise
            # todo: see mvm_main.py
            for k in range(entryDisplays):
                currentRunLine = "\t  " + str(timedelta(seconds=int(workingMap_SpeedrunSplit[j][k]["time"])))[2:] + " | " + datetime.utcfromtimestamp(workingMap_SpeedrunSplit[j][k]["timeAdded"]).strftime('%d-%m-%Y') + " | "
                playersCurrentRunLine = ""
                for l in range(len(workingMap_SpeedrunSplit[j][k]["players"])):
                    if k == 0:
                        firstPlaceRunners.append(str(workingMap_SpeedrunSplit[j][k]["players"][l]["personaname"]))
                    playersCurrentRunLine = playersCurrentRunLine + mvm.shorten_string(str(workingMap_SpeedrunSplit[j][k]["players"][l]["personaname"]), 20) + ", "
                if l > 5:
                    currentRunLine = currentRunLine + "(BUGGED) " + playersCurrentRunLine
                else:
                    currentRunLine = currentRunLine + playersCurrentRunLine
                writingList.append(currentRunLine[:-2])
        writingList.append("")
writingList.append("== Stats ==\n\nMaps: " + str(len(map_list)) + "\nMissions: " + str(len(mission_list)) + "\n\nTop 10 runners (by most #1s):")
firstPlaceRunners = Counter(firstPlaceRunners).most_common(10)
# this will technically break if you run it on a *very* unpopulated speedrun ladder
for i in range(10):
    writingList.append("  " + str(firstPlaceRunners[i][0]) + ": " + str(firstPlaceRunners[i][1]))
writingList.append("")

# SAVE RESULT
if not path.exists('./output/'):
    makedirs('./output/')
with open('./output/' + fileSaveName, mode='wt', encoding='utf-8') as outputFile:
    outputFile.write('\n'.join(writingList))
print("All speedruns saved to \"" + path.abspath('./output/' + fileSaveName) + "\".")

# == END ==
