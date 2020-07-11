from leaguepedia_sb_parser.riot_parser import RiotParser
from leaguepedia_sb_parser.chinese_parser import ChineseParser
from river_mwclient.esports_client import EsportsClient
from river_mwclient.auth_credentials import AuthCredentials
import logging

credentials = AuthCredentials(user_file="me")
site = EsportsClient('lol', credentials=credentials)

riot_parser = RiotParser(site, 'LCK/2020 Season/Summer Season')
chinese_parser = ChineseParser(site, 'LPL/2020 Season/Summer Season')

# print(riot_parser.parse_series(['https://matchhistory.na.leagueoflegends.com/en/#match-details/ESPORTSTMNT01/1415112?gameHash=bb66036323278a5c&tab=overview', 'https://matchhistory.na.leagueoflegends.com/en/#match-details/ESPORTSTMNT01/1415168?gameHash=552fc6b68f1c6847&tab=overview']))

print(chinese_parser.parse_series('https://lpl.qq.com/es/stats.shtml?bmid=6200'))

print(chinese_parser.warnings)
