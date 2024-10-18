from flask import Flask, render_template, request, url_for, flash, redirect
from datetime import datetime
import sqlite3
import logging


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
        try:
            datetime.strptime(details[1], date_format)
        except:
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

        date_format = "%d/%m"
        try:
            datetime.strptime(details[1], date_format)
        except:
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

# App Settings
logging.basicConfig(filename="logs/app.log",
                            format="%(asctime)s %(message)s")

# MIGHT DELETE
log = logging.getLogger("werkzeug")
log.disabled = True

app = Flask(__name__)

# should be a long random string: generate one
app.config['SECRET_KEY'] = '18910406653483515110288420272555'
app.logger.setLevel(logging.INFO)

# App functions
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
                app.logger.info(f"Client successfully created team entries")
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
                    app.logger.info(f"Client successfully created match entries")
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
    if request.method == 'POST':
        
        team_info = request.form['team-info']
        match_results = request.form['match-results']
        if not team_info and not match_results:
            flash('No input!')
        else:
            conn = get_db_connection()
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
            else:
                # If it's valid then only insert teams
                for details in team_details:
                    conn.execute('UPDATE team_details SET reg = ?, group_num = ? WHERE team_name = ?',
                                (details[1], int(details[2]), details[0]))
                    app.logger.info(f"Client updated info on {details[0]} to Reg: {details[1]}, Group: {int(details[2])}")
                conn.commit()
                if team_details:
                    flash('Teams Editted!')


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
                    conn.execute('UPDATE match_details SET goals = ?, result = ? WHERE player_one = ? AND player_two = ?',
                                (details[2], details[3], details[0], details[1]))
                    app.logger.info(f"Client updated info on match between {details[0]}-{details[1]} to Result: {details[3]}, Goals: {details[2]}")

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
            app.logger.info(f"Client requesting info on {team_name}")
            conn = get_db_connection()
            exists = conn.execute('SELECT * FROM team_details where team_name = ?',
                                (team_name,)).fetchone()
            if exists == None:
                flash("No such team")
                app.logger.info(f"{team_name} does not exist")
                conn.commit()
                conn.close()
                
            else:
                app.logger.info(f"Sending info on {team_name}")
                res = f"Registration Date: {exists['reg']}<br> Group: {exists['group_num']}<br>Matches:<br>"
                games = conn.execute('SELECT * FROM match_details where player_one = ?',
                                (team_name,)).fetchall()
                
                game_output = []
                for game in games:
                    game_output.append(f"&emsp;{game['result']} against {game['player_two']} with {game['goals']} goals<br>")
                
                game_output.sort()
                conn.commit()
                conn.close()
                
                return render_template('getinfo.html', curr_info=res + "".join(game_output))

    return render_template('getinfo.html', curr_info="")

@app.route('/rankings', methods=["GET",'POST'])
def rankings():
    app.logger.info("Client requesting rankings")
    groups = [[], []]
    
    conn = get_db_connection()
    all_teams = conn.execute('SELECT * from team_details').fetchall()

    # Initialise list for each group
    for team in all_teams:
        group = groups[team['group_num']-1]

        # points, goals, alternate match points, registration date, name
        result = [0, 0, 0, team['reg'], team['team_name']]

        games = conn.execute('SELECT * from match_details WHERE player_one = ?',
                             (team['team_name'],))
        
        # Extract information
        for game in games:
            result[1] -= game['goals']
            if game['result'] == 'Win':
                result[0] -= 3
                result[2] -= 5
            elif game['result'] == 'Draw':
                result[0] -= 1
                result[2] -= 3
            else:
                result[2] -= 1

        group.append(result)

    conn.commit()
    conn.close()

    groups[0].sort()
    groups[1].sort()

    group_one_result = ""
    group_two_result = ""
    for i in range(len(groups[0])):
        result = groups[0][i]
        temp = f"<tr><td>{i+1}</td><td>{result[-1]}</td><td>{-result[0]}</td><td>{-result[1]}</td><td>{-result[2]}</td>"
        if i < 4:
            temp += f"<td>QUALIFIES</td></tr>"
        else:
            temp += f"<td>DOES NOT QUALIFY</td></tr>"
        group_one_result += temp
    
    for i in range(len(groups[1])):
        result = groups[1][i]
        temp = f"<tr><td>{i+1}</td><td>{result[-1]}</td><td>{-result[0]}</td><td>{-result[1]}</td><td>{-result[2]}</td>"
        if i < 4:
            temp += f"<td>QUALIFIES</td></tr>"
        else:
            temp += f"<td>DOES NOT QUALIFY</td></tr>"
        group_two_result += temp
    
    return render_template('rankings.html', group_one_result=group_one_result, group_two_result=group_two_result)

@app.route('/clear', methods=["GET",'POST'])
def clear():
    if request.method == 'POST':
        app.logger.info(f"Client requesting to clear all")
        # delete from database
        conn = get_db_connection()
        with open("./db/schemas.sql") as file:
            conn.executescript(file.read())
        
        conn.commit()
        conn.close()

        flash("All information has been cleared!")
        return redirect(url_for('index'))

    return render_template('clear.html')
      
        