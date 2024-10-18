DROP TABLE IF EXISTS team_details;

CREATE TABLE team_details (
    name VARCHAR PRIMARY KEY,
    reg VARCHAR,
    group INTEGER
);

DROP TABLE IF EXISTS matches;

CREATE TABLE match_details (
    player_one VARCHAR PRIMARY KEY,
    player_two VARCHAR,
    goals INTEGER,
    result VARCHAR
);
