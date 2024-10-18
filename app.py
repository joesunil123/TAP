from flask import Flask, render_template, request, url_for, flash, redirect
from datetime import datetime
import sqlite3


# Helper functions

def get_db_connection():
    conn = sqlite3.connect('./db/data.db')
    conn.row_factory = sqlite3.Row
    return conn

def enter_details(info : str, conn):
    lines = info.splitlines()

    all_details = []
    seen = set()

    for line in lines:
        details = line.split()

        # Verify that the details follow the correct format
        valid_res = valid_details(details, True, conn)
        if(valid_res < 4):
            return None, valid_res
        
        if(details[0] in seen):
            return None, 3
        
        seen.add(details[0])

        all_details.append(details)
            
    return all_details, valid_res

def valid_details(details, is_detail):
    if len(details) != 4:
        return 0
    
    if is_detail:
        # 0 -> Malformed request, 1 -> Invalid date_time, 2-> Invalid group, 3-> Already registered or group is too large, 4 -> Success

        # Check if its a valid date
        date_format = "%d/%m"
        if not bool(datetime.strptime(details[1], date_format)):
            return 1

        # Check if group number is valid
        if details[2] != "0" or details[2] != "1":
            return 2
        

        # TODO: Convert to a DB version
        # # Check if you are inserting something in a group that is too large now
        # if details[0] in self.team_details or self.count[int(details[2])] == 6:
        #     return False

        return 4

    else:
        # 0 -> Malformed request, 1 -> Invalid Score, 2 -> Not on the same team, 3 -> Not registered OR already played, 4 -> Success

        # Check scores of match
        if not details[2].isnumeric() or not details[3].isnumeric():
            return 0
        
        if int(details[2]) < 0 or int(details[3]) < 0:
            return 1
        
        # TODO: Convert to DB
         # Check if they are on the same team
        # if self.team_details[details[0]][1] != self.team_details[details[1]][1]:
        #     return 2
        
        # # Check if the teams are already registered
        # if details[0] not in self.team_details or details[1] not in self.team_details:
        #     return 3
        
        return 4
        
def enter_matches(info : str, conn):
    lines = info.splitlines()
    seen = set()
    all_details = []

    for line in lines:
        details = line.split()

        # Verify that the details follow the correct format
        valid_res = valid_details(details, False, conn)
        if(valid_res < 4):
            return None, valid_res
        
        if((details[0], details[1]) in seen or (details[1], details[0]) in seen):
            return None, 3
        
        seen.add((details[0], details[1]))
        
        goals_one = int(details[2])
        goals_two = int(details[3])
        res_one = [details[0], details[1], goals_one]
        res_two = [details[1], details[0], goals_two]
        if(goals_one > goals_two):
            res_one.append("Win")
            res_two.append("Loss")
        elif(goals_one < goals_two):
            res_one.append("Loss")
            res_two.append("Win")
        else:
            res_one.append("Draw")
            res_two.append("Draw")


        all_details.append(res_one)
        all_details.append(res_two)
    
    return all_details
        

# App functions
app = Flask(__name__)
# should be a long random string: generate one
app.config['SECRET_KEY'] = 'your secret key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=('POST'))
def create():
    if request.method == 'POST':
        team_info = request.form['team-info']
        match_results = request.form['match-results']
        
        if not team_info:
            flash('Team info is required!')
        elif not match_results:
            flash('Match results are required!')
        else:
            conn = get_db_connection()
            team_details = None
            match_details = None

            # First perform for the the team details
            team_details, valid_input = enter_details(team_info, conn)
            if team_details == None:
                if valid_input == 0:
                    flash('Team info: Malformed request!')
                elif valid_input == 1:
                    flash('Team info: Invalid datetime format on one or more lines')
                elif valid_input == 2:
                    flash('Team info: Invalid group on one or more teams')
                elif valid_input == 3:
                    flash('Team info: Contains an already registered team OR group is too large')
            else:
                match_details, valid_input = enter_matches(match_results, conn)
                if match_details == None:
                    if valid_input == 0:
                        flash('Match info: Malformed request!')
                    elif valid_input == 1:
                        flash('Match info: Invalid Score')
                    elif valid_input == 2:
                        flash('Match info: Some teams are not in the same group')
                    elif valid_input == 3:
                        flash('Match info: Some teams are not registered or have already played')

            if team_details != None and match_details != None:
                for details in team_details:
                    conn.execute('INSERT INTO team_details (name, reg, group) VALUES (?, ?, ?)',
                                (details[0], details[1], int(details[2])))
                        
                for details in match_details:
                    conn.execute('INSERT INTO match_details (player_one, player_two, goals, result) VALUES (?, ?, ?, ?)',
                                (details[0], details[1], details[2], details[3]))
                print("Submitted form!")
                conn.commit()
                conn.close()
                return redirect(url_for('index'))
            conn.commit()
            conn.close()
            pass
    return render_template('create.html')

@app.route('/edit', methods=('GET', 'POST'))
def edit():
    curr_info = {"team-info" : "string with curr team info", "match-results":"string with curr match results"}
    
    if request.method == 'POST':
        team_info = request.form['team-info']
        match_results = request.form['match-results']

        if not team_info:
            flash('Team info is required!')
        elif not match_results:
            flash('Match results are required!')
        else:
            print("submitted form")
            # process and add to databse here!!
            pass

    return render_template('edit.html', curr_info=curr_info)

@app.route('/clear', methods=('GET', 'POST'))
def clear():
    if request.method == 'POST':
        # delete from database
        pass

    return render_template('clear.html')
      
        