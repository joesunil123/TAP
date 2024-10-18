DROP TABLE IF EXISTS team_details;
DROP TABLE IF EXISTS match_details;

CREATE TABLE team_details (
    team_name VARCHAR(50) PRIMARY KEY,
    reg VARCHAR(50) NOT NULL,
    group_num INTEGER NOT NULL
);

CREATE TABLE match_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_one VARCHAR(50) NOT NULL,
    player_two VARCHAR(50) NOT NULL,
    goals INTEGER NOT NULL,
    result VARCHAR(6) NOT NULL
);
