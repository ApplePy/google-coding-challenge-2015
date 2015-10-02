# Darryl Murray, Code: 0085D1
# Google Coding Challenge, September 25, 2015

# Description: This program takes a JSON-formatted file from the command line and outputs a JSON string
# to the console of which users should be allocated storage and how many TB of storage they should receive.

# Process: The program receives the JSON file to be read from the command line. This is retrieved via sys.argv
# and sent to importJSON to read the file and return a JSON object. From there, this object is passed to
# weighting() to rank the users based on the criteria I chose, using several loops to strip out users
# that don't contribute enough, and this function returns the list of users with their rankings,
# and the total of the rankings. The results are then normalized to some #/1000TB, and printed out.
# I used python for it's built-in JSON support and easy-to-get-started nature, allowing me to focus less
# on language quirks.

# Bugs/Odd Behaviour that I ran out of time to fix:
# --> On certain values of __numOfUsersToAward__, all users that were assigned storage
# got 2TB.
# --> Occasionally not all of the 1000TB was allocated to users

import sys
import json

__storageSize__ = 1000
__numOfUsersToAward__ = 700  # This value is arbitrary
__plusOnesWeight__ = 0.6  # Most important to community health
__postsWeight__ = 0.3
__circlesWeight__ = 0.1  # Least important to community health


# Function reads a JSON-formatted file and returns a JSON object
def importJSON(fileName):
    fileHandle = open(fileName)
    jsonData = json.load(fileHandle)
    fileHandle.close()  # Close the file since its no longer needed
    return jsonData


# This function takes a dict object of users to weight, and returns a list of the users with their weighting,
# and the total of all the weighting values (to make it simple later to translate the weighting to TB given).
# This function used the priority variables listed at the top to weight how important a user's attributes
# were to the decision of giving them free storage.
def weighting(inputDict):
    average = 0  # stores the average weighting
    count = 0  # stores how many users have been looked at so far
    total = 0  # stores the total value of the rankings of users looked at
    userDict = {}

    for keys in inputDict:  # Weight how different users contribute to the community health of G+
        count += 1
        userDict[keys] = int(inputDict[keys]['numPlusOnes'] * __plusOnesWeight__ +
                         inputDict[keys]['numPosts'] * __postsWeight__ +
                         len(inputDict[keys]['circles']) * __circlesWeight__)
        total += userDict[keys]
        average = (average * (count - 1) + userDict[keys]) / count  # Continuously updated average

    # Only want above-average contributors to G+; delete the rest from consideration
    # This is to cut down the list so that everyone left gets some free storage
    while len(userDict) > __numOfUsersToAward__:
        total = 0
        count = 0
        numToDelete = len(userDict) - __numOfUsersToAward__
        usersDeleted = 0
        newAverage = 0
        newDict = {}

        for keys in userDict:
            count += 1

            if userDict[keys] <= average and usersDeleted < numToDelete:
                usersDeleted += 1
            else:
                newDict[keys] = userDict[keys]
                total += newDict[keys]
                newAverage = (newAverage * (count - 1) + newDict[keys]) / count

        # Prep for another loop
        average = newAverage
        userDict = newDict

    # Add in the removed users, with 0TB of storage
    for user in inputDict:
        if user not in userDict.keys():
            userDict[user] = 0

    return {'list': userDict, 'total': total}

# Make sure there was a file specified
if len(sys.argv) < 2:
    print "There was no input specified!"
    sys.exit(0)
elif len(sys.argv) > 2:
    print "Too many arguments!"
    sys.exit(0)

# Since a valid input was given, read the JSON in
fileInput = importJSON(sys.argv[1])

# Produce an arbitrary weighting system for the users, that can be normalized to 1000TB
weightedOutput = weighting(fileInput)
woList = weightedOutput["list"]  # Make life a little bit easier
woTotal = weightedOutput["total"]

# Normalize the weighted output to 1000TB
for user in woList:
    woList[user] = float(woList[user] * __storageSize__) / woTotal
    if woList[user] - int(woList[user]) > 0.5:  # deal with rounding issue
        woList[user] += 0.5
    woList[user] = int(woList[user])

# Output the storage allocations
print json.dumps(woList, sort_keys=True)
