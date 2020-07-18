from leaguepedia_sb_parser.riot_parser import RiotParser
from leaguepedia_sb_parser.chinese_parser import ChineseParser
from river_mwclient.esports_client import EsportsClient
from river_mwclient.auth_credentials import AuthCredentials
from lol_esports_parser import get_riot_game

credentials = AuthCredentials(user_file="me")
site = EsportsClient('lol', credentials=credentials)

riot_parser = RiotParser(site, 'VCS 2020 Summer')
chinese_parser = ChineseParser(site, 'LPL/2020 Season/Summer Season')

print(riot_parser.parse_series(['https://matchhistory.na.leagueoflegends.com/en/#match-details/ESPORTSTMNT03/1405985?gameHash=43f50700a480e443&tab=overview']))

# print(chinese_parser.parse_series('6200'))

# print(chinese_parser.warnings)

# with open('data.txt', 'w') as f:
#     f.write(str(get_riot_game('https://matchhistory.na.leagueoflegends.com/en/#match-details/ESPORTSTMNT03/1404937?gameHash=bda3b01d3514ad28&tab=overview', get_timeline=True)))
