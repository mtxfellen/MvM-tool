from os import path
from mvm_main import net_request

print("Retrieving mission information...")
mission_list = net_request('https://archive.potato.tf/api/missioninfo','json')
writingList = []

for i in range(len(mission_list)):
    writingList.append("{\n\t\"mission\":\"" + mission_list[i]["mission"] + "\"\n\t\"readytime\":10\n\t\"tags\":\"\"\n},")
writingList[0] = "[" + writingList[0]
writingList[-1] = writingList[-1][:-1] + "]"

if path.isfile('mission-tags.json'):
    raise SystemExit('\'mission-tags.json\' already exists.')
with open('mission-tags.json', mode='wt', encoding='utf-8') as outputFile:
    outputFile.write('\n'.join(writingList) + '\n')
print("Skeleton tags saved to \"" + path.abspath('mission-tags.json') + "\".")
