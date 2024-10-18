from flask import Flask, render_template, request, url_for, flash, redirect
from datetime import datetime
import sqlite3


# Helper functions

def get_db_connection():
    conn = sqlite3.connect('./db/data.db')
    conn.row_factory = sqlite3.Row
    return conn

def enter_details(info : str, conn):
    if not info:
        return [], 4
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

def valid_details(details, is_detail, conn):
    if is_detail:
        # 0 -> Malformed request, 1 -> Invalid date_time, 2-> Invalid group, 3-> Already registered or group is too large, 4 -> Success
        if len(details) != 3:
            return 0
        # Check if its a valid date
        date_format = "%d/%m"
        #TODO: Fix this
        if not bool(datetime.strptime(details[1], date_format)):
            return 1

        # Check if group number is valid
        if details[2] != "2" and details[2] != "1":
            return 2
        
        exists = conn.execute('SELECT * FROM team_details where team_name = ?',
                              (details[0],)).fetchone()
        if exists != None:
            return 3
        
        count = conn.execute('SELECT * FROM team_details where group_num = ?',
                            (int(details[2]),)).fetchall()
        
        if count != None and len(count) >= 6:
            return 3

        return 4

    else:
        # 0 -> Malformed request, 1 -> Invalid Score, 2 -> Not on the same team, 3 -> Not registered OR already played, 4 -> Success
        if len(details) != 4:
            return 0
        
        # Check scores of match
        if not details[2].isnumeric() or not details[3].isnumeric():
            return 0
        
        if int(details[2]) < 0 or int(details[3]) < 0:
            return 1
        
        # TODO: Convert to DB
        team_one = conn.execute('SELECT * FROM team_details where team_name = ?',
                              (details[0],)).fetchone()

        team_two = conn.execute('SELECT * FROM team_details where team_name = ?',
                              (details[1],)).fetchone()
        
        if team_one == None or team_two == None:
            return 3
        
        if team_one['group_num'] != team_two['group_num']:
            return 2
        
        exists = conn.execute('SELECT * FROM match_details where player_one = ? and player_two = ?',
                              (details[0], details[1])).fetchone()
        if exists != None:
            return 3
        
        return 4
        
def enter_matches(info : str, conn):
    if not info:
        return [], 4
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
    
    return all_details, 4
        
def edit_details(info : str, conn):
    if not info:
        return [], 4
    lines = info.splitlines()

    all_details = []

    for line in lines:
        details = line.split()

        # Verify that the details follow the correct format
        if len(details) != 3:
            return None, 0

        #TODO: Fix this
        date_format = "%d/%m"
        if not bool(datetime.strptime(details[1], date_format)):
            return None, 1
        
        if details[2] != "2" and details[2] != "1":
            return None, 2
        
        exists = conn.execute('SELECT * FROM team_details where team_name = ?',
                              (details[0],)).fetchone()
        if exists == None:
            return None, 3
        
        
        all_details.append(details)
    return all_details, 4

def edit_matches(info : str, conn):
    if not info:
        return [], 4
    lines = info.splitlines()
    seen = set()
    all_details = []

    for line in lines:
        details = line.split()

        if len(details) != 4:
            return None, 0
        
        # Check scores of match
        if not details[2].isnumeric() or not details[3].isnumeric():
            return None, 0
        
        if int(details[2]) < 0 or int(details[3]) < 0:
            return None, 1
        
        exists = conn.execute('SELECT * FROM match_details where player_one = ? and player_two = ?',
                              (details[0], details[1])).fetchone()

        if exists == None:
            return None, 2
        
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

    return all_details, 4

# App functions
app = Flask(__name__)
# should be a long random string: generate one
app.config['SECRET_KEY'] = 'your secret key'
app.debug = True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=["GET","POST"])
def create():
    if request.method == 'POST':
        team_info = request.form['team-info']
        match_results = request.form['match-results']
        
        if not team_info and not match_results:
            flash('No input!')
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
                # If it's valid then only insert teams
                for details in team_details:
                    conn.execute('INSERT INTO team_details (team_name, reg, group_num) VALUES (?, ?, ?)',
                                (details[0], details[1], int(details[2])))
                conn.commit()
                if team_details:
                    flash('Teams submitted!')
                    
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
            else:
                for details in match_details:
                    conn.execute('INSERT INTO match_details (player_one, player_two, goals, result) VALUES (?, ?, ?, ?)',
                                (details[0], details[1], details[2], details[3]))
                conn.commit()
                if match_details:
                    flash('Matches submitted!')
            conn.close()
            pass
        if match_details != None and team_details != None:
            return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/edit', methods=["GET",'POST'])
def edit():
    # curr_info = {"team-info" : "string with curr team info", "match-results":"string with curr match results"}
    
    if request.method == 'POST':
        team_info = request.form['team-info']
        match_results = request.form['match-results']
        print("Step 1")
        if not team_info and not match_results:
            flash('No input!')
        else:
            conn = get_db_connection()
            print("Step 3")
            team_details = None
            match_details = None


            team_details, valid_input = edit_details(team_info, conn)
            if team_details == None:
                if valid_input == 0:
                    flash('Team info: Malformed request!')
                elif valid_input == 1:
                    flash('Team info: Invalid datetime format on one or more lines')
                elif valid_input == 2:
                    flash('Team info: Invalid group on one or more teams')
                elif valid_input == 3:
                    flash('Team info: No such team')
                print("FAIL")
            else:
                # If it's valid then only insert teams
                for details in team_details:
                    conn.execute('UPDATE team_details SET reg = ?, group_num = ? WHERE team_name = ?',
                                (details[1], int(details[2]), details[0]))
                conn.commit()
                if team_details:
                    flash('Teams Editted!')

                print("SUCCESS")

            match_details, valid_input = edit_matches(match_results, conn)
            if match_details == None:
                if valid_input == 0:
                    flash('Match info: Malformed request!')
                elif valid_input == 1:
                    flash('Match info: Invalid Score')
                elif valid_input == 2:
                    flash('Match info: No such game')
            else:
                for details in match_details:
                    conn.execute('INSERT INTO match_details (player_one, player_two, goals, result) VALUES (?, ?, ?, ?)',
                                (details[0], details[1], details[2], details[3]))
                conn.commit()
                if match_details:
                    flash('Matches Editted!')
            conn.close()

        if match_details != None and team_details != None:
            return redirect(url_for('index'))
    return render_template('edit.html')

@app.route('/getinfo', methods=["GET",'POST'])
def getinfo():
    if request.method == 'POST':
        team_name = request.form['team-name']
        if not team_name:
            flash("No input")
        else:
            conn = get_db_connection()
            exists = conn.execute('SELECT * FROM team_details where team_name = ?',
                                (team_name,)).fetchone()
            if exists == None:
                
                flash("No such team")
                conn.commit()
                conn.close()
                
            else:
                res = f"Registration Date: {exists['reg']}<br> Group: {exists['group_num']}<br>Matches:<br>"
                games = conn.execute('SELECT * FROM match_details where player_one = ?',
                                (team_name,)).fetchall()
                
                game_output = []
                for game in games:
                    game_output.append(f"&emsp;{game['result']} against {game['player_two']} with {game['goals']} goals<br>")
                
                game_output.sort()
                conn.commit()
                conn.close()
                
                return render_template('getinfo.html', curr_info="".join(game_output))

    return render_template('getinfo.html', curr_info="")

@app.route('/rankings', methods=["GET",'POST'])
def rankings():
    pass

@app.route('/clear', methods=["GET",'POST'])
def clear():
    if request.method == 'POST':
        # delete from database
        conn = get_db_connection()
        with open("./db/schemas.sql") as file:
            conn.executescript(file.read())
        
        conn.commit()
        conn.close()

        flash("All information has been cleared!")
        return redirect(url_for('index'))

    return render_template('clear.html')
      
        