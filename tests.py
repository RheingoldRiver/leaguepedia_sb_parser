from leaguepedia_sb_parser.riot_parser import RiotParser
from leaguepedia_sb_parser.chinese_parser import ChineseParser
from river_mwclient.esports_client import EsportsClient
from river_mwclient.auth_credentials import AuthCredentials
from lol_esports_parser import get_riot_game

credentials = AuthCredentials(user_file="me")
site = EsportsClient('lol', credentials=credentials)

riot_parser = RiotParser(site, 'GUL 2020 Closing Playoffs')
# chinese_parser = ChineseParser(site, 'LPL/2020 Season/Summer Season')

print(riot_parser.parse_series(['https://matchhistory.na.leagueoflegends.com/en/#match-details/ESPORTSTMNT01/1434268?gameHash=6a9d4306ee294f85&tab=overview']))

# print(chinese_parser.parse_series('https://www.wanplus.com/schedule/63545.html'))

with open('data.txt', 'w') as f:
    f.write(str(get_riot_game('https://matchhistory.na.leagueoflegends.com/en/#match-details/ESPORTSTMNT01/1434268?gameHash=6a9d4306ee294f85&tab=overview', get_timeline=True, add_names=True)))
