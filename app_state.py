import logging
import heapq as heap
from datetime import datetime


# Want to support editing details
# Want to support editing match details
# We will assume for now that once a team is set to be part of group A it is permanently part of group A
# Breaks ties alphabetically

class GameState():

    def __init__(self):
        # Create logger
        logging.basicConfig(filename="logs/game_state.log",
                            format="%(asctime)s %(message)s")
        
        self.logger = logging.getLogger()

        # Information on registration, group, who they played against and what was the outcome
        self.team_details = {}
        self.team_count = [0,0]

    # Returns True if the details are entered correctly confirming change of state, else return False
    def EnterDetails(self, info : str):
        lines = info.splitlines()

        allDetails = []

        for line in lines:
            details = line.split()

            # Verify that the details follow the correct format
            if not self.ValidDetails(details, True):
                # TODO: Log
                return False
            
            allDetails.append(details)

        # Details are valid so edit the state
        for details in allDetails:
        
            if details[0] in self.team_details:
                self.team_details[details[0]][1] = details[1]

                # TODO: Log
            else:
                self.team_details[details[0]] = [details[1], int(details[2]), {}]
                self.count[int(details[2])] += 1

                # TODO: Log

        return True
    
    def ValidDetails(self, details, is_detail):
        if len(details) != 4:
            return False
        
        if is_detail:

            # Check if its a valid date
            date_format = "%d/%m"
            if not bool(datetime.strptime(details[1], date_format)):
                return False

            # Check if group number is valid
            if details[2] != "0" or details[2] != "1":
                return False
            
            # Check if you are inserting something in a group that is too large now
            if details[0] in self.team_details or self.count[int(details[2])] == 6:
                return False

            return True

        else:
            # Check if the teams are already registered
            if details[0] not in self.team_details or details[1] not in self.team_details:
                return False
            
            # Check if they are on the same team
            if self.team_details[details[0]][1] != self.team_details[details[1]][1]:
                return False
            
            # Check scores of match
            if not details[2].isnumeric() or not details[3].isnumeric():
                return False
            
            return int(details[2]) >= 0 and int(details[3]) >= 0

    def EnterMatches(self, info : str):
        lines = info.splitlines()

        allDetails = []

        for line in lines:
            details = line.split()

            # Verify that the details follow the correct format
            if not self.ValidDetails(details, False):
                # TODO: Log
                return False
        
            allDetails.append(details)
        
        for details in allDetails:
            
            # Extract the group number
            self.EditMatchDetails(details[0], details[1], int(details[2]), int(details[3]))

    def EditMatchDetails(self, team_one, team_two, goals_one, goals_two):
        if goals_one > goals_two:
            self.team_details[team_one][team_two] = ("Win", goals_one)
            self.team_details[team_two][team_one] = ("Loss", goals_two)
        elif goals_two > goals_one:
            self.team_details[team_one][team_two] = ("Loss", goals_one)
            self.team_details[team_two][team_one] = ("Win", goals_two)
        else:
            self.team_details[team_one][team_two] = ("Draw", goals_one)
            self.team_details[team_two][team_one] = ("Draw", goals_two)

        # TODO: Log
            
    def GetTeamDetails(self, team_name):

        # TODO: We have to strip any trailing spaces, tabs, newlines
        details = self.team_details.get(team_name)

        if details is None:
            return None
        res = f"Registration Date: {details[0]}\n Group: {details[1]}\n Matches Played:\n"
        for opp, result in details[2].items():
            res += f"\t{opp}: {result[0]}"
        
        # TODO: Log the request
            
        return res
    
    def GetRankings(self):
        group_teams = [[], []]
        total_alt = [0, 0]
        teams = {}

        for team, details in self.team_details.items():
            group_teams[details[1]].append(team)

            # teams[team] = [0, 0, 0, ]

    def ClearAll(self):

        self.team_details = {}
        self.team_count = [0,0]

        # TODO: Some way to clear logs



if __name__ == "main":
    print("x")