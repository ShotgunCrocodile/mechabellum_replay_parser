# What is this

A basic replay file parser for mechabellum replay files (.grbr).

# Usage

Currently I have only tested it on python 3.9. You will need to install prettytable in order for it to work.

```
python -m pip install -r requirements.txt
```

Once you have the dependencies in your python environment you can point it at a replay file like so:

```
$ python .\mechabellum_replay_parser.py 'C:\Program Files (x86)\Steam\steamapps\common\Mechabellum\ProjectDatas\Replay\1475_20250110--134322461_[ShotgunCrocodile]VS[Opponent].grbr'
```
 
And it should spit out a table that looks like this:

```
+------+-----------------------------------+----------------------------------+
| Round| ShotgunCrocodile                  | Opponent                         |
+------+-----------------------------------+----------------------------------+
| 0    | Typhoon Specialist                | Amplify Specialist               |
|      | fang                              | sabertooth                       |
|      | fang                              | sabertooth                       |
|      | fang                              | arclight                         |
|      | stormcaller                       | arclight                         |
|      | stormcaller                       | arclight                         |
+------+-----------------------------------+----------------------------------+
| 1    | Unlock arclight                   | Unlock crawler                   |
|      | Buy arclight                      | Buy crawler                      |
|      | Buy arclight                      | Buy crawler                      |
+------+-----------------------------------+----------------------------------+
| 2    | Buy arclight                      | Unlock fang                      |
|      | Buy fang                          | Buy fang                         |
|      | Unlock crawler                    | Buy crawler                      |
|      | Command Tower Mass Recruit        |                                  |
|      | Buy crawler                       |                                  |
+------+-----------------------------------+----------------------------------+
| 3    | Unlock phoenix                    | Upgrade sabertooth               |
|      | Buy phoenix                       | Buy arclight                     |
|      | Research Tower Field Recovery     | Buy fang                         |
|      | Buy crawler                       | Upgrade arclight                 |
|      | Command Tower Mass Recruit        | Unlock marksmen                  |
|      | Buy crawler                       | Command Tower Mass Recruit       |
|      |                                   | Buy crawler                      |
+------+-----------------------------------+----------------------------------+
| 4    | Upgrade arclight                  | Unlock mustang                   |
|      | Upgrade arclight                  | Buy mustang                      |
|      | Tech arclight Range               | Tech mustang Range               |
|      | Buy arclight                      | Research Tower Field Recovery    |
|      | Buy fang                          | Command Tower Elite Recruit      |
|      | Command Tower Mass Recruit        | Command Tower Loan               |
|      | Buy fang                          | Buy mustang                      |
|      |                                   | Research Tower Attack Enhancement|
|      |                                   | Upgrade arclight                 |
+------+-----------------------------------+----------------------------------+
| 5    | Device Shield Generator           | Buy crawler                      |
|      | Unlock steel ball                 | Buy mustang                      |
|      | Buy crawler                       | Tech arclight Range              |
|      | Buy steel ball                    |                                  |
|      | Command Tower Mass Recruit        |                                  |
|      | Buy crawler                       |                                  |
|      | Upgrade phoenix                   |                                  |
|      | Upgrade arclight                  |                                  |
|      | Research Tower Attack Enhancement |                                  |
|      | Research Tower Oil Bomb           |                                  |
|      | Research Tower Defence Enhancement|                                  |
+------+-----------------------------------+----------------------------------+
| 6    | Upgrade steel ball                | Tech crawler Impact Drill        |
|      | Upgrade wasp                      | Upgrade mustang                  |
|      | Buy wasp                          | Buy fortress                     |
|      | Buy steel ball                    | Buy crawler                      |
|      | Upgrade arclight                  | Command Tower Mass Recruit       |
|      | Command Tower Mass Recruit        | Command Tower Loan               |
|      | Buy arclight                      | Tech fortress Barrier            |
|      | Upgrade typhoon                   | Command Tower High Mobility      |
+------+-----------------------------------+----------------------------------+
| 7    | Device Shield Generator           | Buy fortress                     |
|      | Upgrade arclight                  | Buy fortress                     |
|      | Upgrade wasp                      | Command Tower Mass Recruit       |
|      | Tech wasp Range                   | Buy mustang                      |
|      | Command Tower Elite Recruit       | Command Tower Loan               |
|      | Buy steel ball                    | Command Tower Enhanced Range     |
|      | Buy steel ball                    | Command Tower High Mobility      |
|      | Command Tower Mass Recruit        | Research Tower Mobile Beacon     |
|      | Buy wasp                          | Upgrade mustang                  |
|      | Command Tower Loan                |                                  |
|      | Device Shield Generator           |                                  |
+------+-----------------------------------+----------------------------------+
```

# Stats calculator

Started a calculator to aggregate information about a player or a replay. Ideally I would like to have the script extract all the data
into a record format that could be fed into a sqlitedb. From there I could add a some scripts here that make accessing the db 
simple. For now though the stats.py simply extracts the only thing I was interested at the time and prints it out. If I get interested
in additional stats I may go through the effort to export to a database.

# Contributing

Theres a lot still missing so feel free to make a pull request too add something. 

If you parse a replay and you get a number for a tech it would be handy if you could make a pull request to add that number to the appropriate lookup table:

Techs: https://github.com/ShotgunCrocodile/mechabellum_replay_parser/blob/main/mechabellum_replay_parser.py#L79

# Similar Projects

IcyD kindly pointed me to their similar project here: https://github.com/IcyIcyD/MechabellumReplayParser where I got a lot of the IDs from.

