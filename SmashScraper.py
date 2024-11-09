from wsgiref import headers

from bs4 import BeautifulSoup
import requests
import gspread

smash_ultimate_characters = [ #Would have to dynamically receive each character name from the site which uses JS to fill the list,
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

names = smash_ultimate_characters
for i in range(len(names)):
    #We now need to change all of the names to fit the link specifications.
    #So spaces must be dashes, periods are removed, and & symbols are shown as "and".
    # print(name)
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

    names[i] = name #Re-stores the name back into names.

# Getting all of the flat character winrates.
stats = []
winStats = dict()
lossStats = dict()
for i in range(5): #Now the goal is to iterate through each character's page and pull their stats.
    link = "https://ultimatestagedata.com/character/" + names[i]
    link = requests.get(link).text
    soup = BeautifulSoup(link, "html.parser")

    # stat = soup.find("div", class_="font-fjalla font-bold text-3xl md:text-2xl lg:text-3xl").text
    #This stat finds the average win/loss rate of the character itself.

    for j in range(3): #Four the first 3 stage types, that being Starter, Counterpick, and retired.
        statblock = soup.find("div", class_ ="relative py-4 flex flex-col items-center flex-1")
        # print(statblock.prettify())
        stageNames = statblock.find_all("h4", class_ = "font-fjalla text-2xl font-bold underline sm:text-3xl")
        stageWin = statblock.find("div", class_="flex-col items-center flex-1")  #TODO: NOT FOUND
        for m in stageNames:
            print(m.text)
        stat = "0 - 0"
        stats.append(stat)
        winStats.update({names[i]: stat.split(" - ")[0]})
        lossStats.update({names[i]: stat.split(" - ")[1]})
        print(names[i])
        # print(stat)  ##Keeping this so that my code keeps up.

print(winStats)
print(lossStats)

#Prepping storage into google sheet.
file = r"C:\Users\blues\AppData\Roaming\gspread\python-smash-datascrapes-dc54bc5fdcee.json"
sa = gspread.service_account(filename = file)
sh = sa.open("Smash-Datascrape-Results")
wks = sh.worksheet("Sheet1")

# namesToColumns = [] #Only need this for printing the matchup names. Leave for now.
# for i in range(len(names)):
#     namesToColumns.append([names[i]])  # Wrap each name in a list
#
# wks.update(namesToColumns, 'E2:E90')
# namesToThirty = [names[:len(names)]]  # A list with a single row containing 30 values
# wks.update(namesToThirty, 'F1:CM1')

#This prints every possible matchup. About 7221.
# for i in range(len(names)): #NOTE: Will be len(names)
#     stats = []
#     for j in range(len(names)): #NOTE: Will be len(names)
#         if names[i] != names[j]:
#             link = "https://ultimatestagedata.com/matchup/" + names[i] + "/" + names[j]
#             # print(link)
#             print(names[i])
#             print(names[j])
#             link = requests.get(link).text
#
#             soup = BeautifulSoup(link, "html.parser")
#             stat = soup.find("div", class_="font-fjalla font-bold text-3xl md:text-2xl lg:text-3xl").text
#             print(stat)
#             stats.append(stat)
#
#     cell_range = 'F' + str(i + 2) + ":CM" + str(i + 2)
#     #Stores the data dynamically per row.
#     wks.update(cell_range, [stats])



# #This will store all of the flat character rates.
# namesToColumns = [] #Only need this for printing. Leave for now.
# lossesToColumns = []
# winsToColumns = []
# for i in range(len(names)):
#     namesToColumns.append([names[i]])  # Wrap each name in a list
#     winStat = winStats.get(names[i])
#     lossStat = lossStats.get(names[i])
#     # print(winStat)
#     # print(lossStat)
#     lossesToColumns.append([winStat])
#     winsToColumns.append([lossStat])
#
# wks.update(namesToColumns, 'A2:A90')
# wks.update(lossesToColumns, 'B2:B90')
# wks.update(winsToColumns, 'C2:C90')














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