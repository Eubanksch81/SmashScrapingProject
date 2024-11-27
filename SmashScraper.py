from enum import unique
from wsgiref import headers

from bs4 import BeautifulSoup
import requests
import gspread

names = [ #Would have to dynamically receive each character name from the site which uses JS to fill the list,
    #So just filled them out manually instead.
    "Banjo & Kazooie", "Bayonetta", "Bowser", "Bowser Jr.", "Byleth", "Captain Falcon",
    "Chrom", "Cloud", "Corrin", "Daisy", "Dark Pit", "Dark Samus", "Diddy Kong",
    "Donkey Kong", "Dr. Mario", "Duck Hunt", "Falco", "Fox", "Ganondorf", "Greninja", "Hero",
    "Ice Climbers", "Ike", "Incineroar", "Inkling", "Isabelle", "Jigglypuff", "Joker", "Kazuya", "Ken", "King Dedede",
    "King K. Rool", "Kirby", "Link", "Little Mac", "Lucario", "Lucas", "Lucina", "Luigi", "Mario",
    "Marth", "Mega Man", "Meta Knight", "Mewtwo", "Mii Brawler", "Mii Gunner", "Mii Swordfighter", "Min Min",
    "Mr. Game & Watch", "Ness", "Olimar", "Pac-man", "Palutena", "Peach", "Pichu",
    "Pikachu", "Piranha Plant", "Pit", "Pokemon Trainer", "Pyra & Mythra", "R.O.B.", "Richter",
    "Ridley", "Robin", "Rosalina", "Roy", "Ryu", "Samus", "Sephiroth",
    "Sheik", "Shulk", "Simon", "Snake", "Sonic", "Sora", "Steve", "Terry", "Toon Link", "Villager",
    "Wario", "Wii Fit Trainer", "Wolf", "Yoshi", "Young Link", "Zelda", "Zero Suit Samus"
]

for i in range(len(names)):
    #We now need to change all of the names to fit the link specifications.
    #So spaces must be dashes, periods are removed, and & symbols are shown as "and".
    name = names[i]
    if name.find(".") == -1 and name.find("&") == -1:
        pass
    else:
        if name.find(".") != -1 and name.find("&") != -1: #Has both characters
            name = name.replace("&", "and")
            name = name.replace(".", "")
        elif name.find(".") != -1: #Has periods
            name = name.replace(".", "")
        else: #Has & symbols
            name = name.replace("&", "and")
    while name.find(" ") != -1: #Removes all whitespaces.
        ## Using a while loop here since some characters have 2-3 spaces.
        name = name.replace(" ", "-")
    name = name.casefold() #Removes all capitalization

    names[i] = name #Re-stores the name back into names. #Ch

stageNames = []
stageWins = []
stageLosses = []
organizedData = dict()

for i in range(len(names)): #Now the goal is to iterate through each character's page and pull their stage stats.
    #Goal is the len(names)
    link = "https://ultimatestagedata.com/character/" + names[i]
    link = requests.get(link).text
    soup = BeautifulSoup(link, "html.parser")
    stat = soup.find("div", class_="font-fjalla font-bold text-3xl md:text-2xl lg:text-3xl").text #Pulls the flat win-rate/loss-rate.

    statblock = soup.find_all("ul", class_="flex flex-row flex-wrap w-full m-2 gap-4 px-6 2xl:px-12 2xl:gap-12")  # Pulls the entire stage data.

    for j in range(len(statblock) - 1): #0-2. Goes up to the three types of stages, not including the low-data stages.
        stageNamesArray = statblock[j].find_all("h4", class_="font-fjalla text-2xl font-bold underline sm:text-3xl") # Gets the stage name.
        for n in stageNamesArray:
            stageNames.append(n.text)
        stageData = statblock[j].find_all("span", class_="pointer-events-auto font-fjalla text-3xl font-bold sm:text-6xl") # Holds the win and loss data.

        m = 0
        while m in range(len(stageData)): #Parses the stageData into corresponding win/loss variables.
            stageWin = stageData[m]
            stageLoss = stageData[m+1]
            stageWins.append(stageWin.text)
            stageLosses.append(stageLoss.text)
            m += 2

    print(i) #Just to keep track of the program.
    stageNames.append("Break")
    stageWins.append("0")
    stageLosses.append("0")

winLossData = [] #Puts the wins and losses into a single variable.
for k in range(len(stageWins)):
    if stageWins[k] != 0:
        stageWins[k] = stageWins[k].replace('%', '')
    winLossData.append(float(stageWins[k]))
    #NOTE: We deleted the loss-data here, for easier use of the data in sheets.
organizedData = {name: {} for name in names} #Instantiates

# Organizes stageData by character and stageName in a nested loop.
oIdx = 0
for name in names:
    for o in range(oIdx, len(stageNames)):
        # oIdx makes sure the next turn of the nested loop starts at the index of where the previous loop ended
        # For each character, create a nested dictionary with stage names as keys
        if stageNames[o] == "Break":
            oIdx += 1
            break
        elif stageNames[o] not in organizedData[name]:
            organizedData[name][stageNames[o]] = []  # initialize list for stage data if not present
        # Append win/loss data to the stage for this character
        organizedData[name][stageNames[o]].append(winLossData[o])
        oIdx += 1

# Prepping storage into google sheet.
file = r"C:\Users\blues\AppData\Roaming\gspread\python-smash-datascrapes-dc54bc5fdcee.json"
sa = gspread.service_account(filename = file)
sh = sa.open("Smash-Datascrape-Results")
wks = sh.worksheet("Sheet2") #Using sheet2 here for stage data. Not using sheet1.

namesToRows = [] #Only need this for printing the character names to the sheet. Leave for now.
for i in range(len(names)):
    namesToRows.append([names[i]])  # Wrap each name in a list
wks.update(namesToRows, 'A2:A90') #E2 - E90 for matchups


# Now we need to organize the stage names to output the stages onto the sheet.
all_stages = set()  # Using a set to automatically handle duplicates
for character, stages in organizedData.items():
    for stage_name in stages.keys():
        all_stages.add(stage_name)
# Convert the set to a list if you need a list format
unique_stages_list = [] #Note: We also need this later for checking stages.
for idx in all_stages:
    unique_stages_list.append(idx)
unique_stages_list = sorted(unique_stages_list) #Now the stages are sorted.
stagesToColumns = [unique_stages_list[:len(unique_stages_list)]]  # A list with a single row containing stage values
wks.update(stagesToColumns, 'B1:P1')

colRange = dict()
asciiVal = 66

for idk in unique_stages_list: #Stores the column value of each stage on the sheet.
    asciiVal = chr(asciiVal)
    colRange.update({idk: asciiVal})
    asciiVal = ord(asciiVal)
    asciiVal += 1

# Now to sort the nested dictionary, so we can output it to the sheet.
sorted_organizedData = {
    character: dict(sorted(stages.items()))
    for character, stages in organizedData.items()
}

# Iterate through sorted_organizedData
dataPrint2D = []
for character, stages in sorted_organizedData.items():
    dataPrint = []
    for stage_name in colRange:
        if stage_name in stages.keys():
            # cellId = colRange.get(stage_name) + str(names.index(character) + 2)
            # print("Id: " + cellId)
            data = sorted_organizedData[character][stage_name]
            # print(data[0])
            dataPrint.append(data[0])
            # wks.update_acell(cellId, dataPrint) #TODO: Cuts short due to request quota. Just need to add the whole row to a single array and print.
            #colRange.get(stage_name)
        else:
            # print("NOT FOUND")
            dataPrint.append(0)
    print(dataPrint)
    cellRange = "B" + str(names.index(character) + 2) + ":O" + str(names.index(character) + 2)
    # wks.update(cellRange, [dataPrint])
    print(dataPrint)
    dataPrint2D.append(dataPrint)

print(dataPrint2D)
wks.update("B2:O87", dataPrint2D)


# Prepping storage into google sheet for matchups.
file = r"C:\Users\blues\AppData\Roaming\gspread\python-smash-datascrapes-dc54bc5fdcee.json"
sa = gspread.service_account(filename=file)
sh = sa.open("Smash-Datascrape-Results")
wks = sh.worksheet("Sheet1")  # Using sheet2 here for stage data. Not using sheet1.

# This prints every possible matchup. About 7221.
for i in range(len(names)):  # NOTE: Will be len(names). Can use a starting range to increment through the list, since it'll
    stats = []
    for j in range(len(names)):  # NOTE: Will be len(names)
        if names[i] != names[j]:
            link = "https://ultimatestagedata.com/matchup/" + names[i] + "/" + names[j]
            # print(link)
            print(names[i])
            print(names[j])
            link = requests.get(link).text

            soup = BeautifulSoup(link, "html.parser")
            stat = soup.find("div", class_="font-fjalla font-bold text-3xl md:text-2xl lg:text-3xl").text
            # print(stat)
            stat = stat[0:5]
            if '%' in stat:
                stat = stat.replace('%', '')
                if ' ' in stat and '-' in stat:
                    stat = stat.replace(' ', '')
                    stat = stat.replace('-', '')
            # print(stat)
            stat = float(stat)
            stats.append(stat)
        else:
            stats.append('')
            print('same')
    cell_range = 'F' + str(i + 2) + ":CM" + str(i + 2)
    # Stores the data dynamically per row.
    wks.update(cell_range, [stats])








#Prepping storage into google sheet for flat rates.
file = r"C:\Users\blues\AppData\Roaming\gspread\python-smash-datascrapes-dc54bc5fdcee.json"
sa = gspread.service_account(filename = file)
sh = sa.open("Smash-Datascrape-Results")
wks = sh.worksheet("Sheet2") #Using sheet2 here for stage data. Not using sheet1.

winStats = dict()

for i in range(len(names)): #Now the goal is to iterate through each character's page and pull their stage stats.
    #Goal is the len(names)
    link = "https://ultimatestagedata.com/character/" + names[i]
    link = requests.get(link).text
    soup = BeautifulSoup(link, "html.parser")
    stat = soup.find("div", class_="font-fjalla font-bold text-3xl md:text-2xl lg:text-3xl").text #Pulls the flat win-rate/loss-rate.
    stat = stat[0:5]
    if '%' in stat:
        stat = stat.replace('%', '')
        if ' ' in stat and '-' in stat:
            stat = stat.replace(' ', '')
            stat = stat.replace('-', '')
    print(stat)
    stat = float(stat)
    winStats[names[i]] = stat



# #This will store all of the flat character rates.
# namesToColumns = [] #Only need this for printing. Leave for now.
winsToColumns = []
for i in range(len(names)):
    # namesToColumns.append([names[i]])  # Wrap each name in a list
    winStat = winStats.get(names[i])
    # print(winStat)
    winsToColumns.append([winStat])

# wks.update(namesToColumns, 'A2:A90')
wks.update(winsToColumns, 'B2:B90')


 ## PRIOR RESEARCH
# Here are some example methods that we can use for our code.
# print('Rows: ', wks.row_count)
# print('Cols: ', wks.col_count)
# print(wks.acell('A9').value)
# print(wks.cell(3, 4).value)
# print(wks.get('A7:E9'))
# print(wks.get_all_values())
# wks.update_acell('B1', "George")
# wks.update('D2:E3', [['Engineering', 'Tennis'], ['Business', 'Pottery']])
# wks.update_acell('F2', '=UPPER(E2)', raw=False)
# wks.delete_rows(25)
#Deletes the 25th row

#These are horizontal names. We'll need them later.
# namesToThirty = [names[:30]]  # A list with a single row containing 30 values
# wks.update(namesToThirty, 'B1:AE1')