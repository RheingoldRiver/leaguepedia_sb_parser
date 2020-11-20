from leaguepedia_sb_parser.riot_parser import RiotParser
from leaguepedia_sb_parser.chinese_parser import ChineseParser
from leaguepedia_sb_parser.multi_series_parser import MultiParser
from river_mwclient.esports_client import EsportsClient
from river_mwclient.auth_credentials import AuthCredentials
from lol_esports_parser import get_riot_game
from lol_esports_parser import get_wp_series
from lol_esports_parser import get_qq_series
import logging

credentials = AuthCredentials(user_file="me")
site = EsportsClient('lol', credentials=credentials)

riot_parser = RiotParser(site, 'GUL 2020 Closing Playoffs')
print(riot_parser.parse_series(['http://matchhistory.na.leagueoflegends.com/en/#match-details/ESPORTSTMNT03/1532710?gameHash=31ec0cdc04907462']))

multi_parser = MultiParser(riot_parser)

multi_parser.parse_multi_series('https://matchhistory.na.leagueoflegends.com/en/#match-details/ESPORTSTMNT01/1423603?gameHash=c67872b8e8b05e51&tab=overview\nhttps://matchhistory.na.leagueoflegends.com/en/#match-details/ESPORTSTMNT01/1423603?gameHash=c67872b8e8b05e51&tab=overview')

# print('<br>'.join(riot_parser.warnings))


# chinese_parser = ChineseParser(site, 'LPL/2020 Season/Summer Season', patch="10.15.1")
# print(chinese_parser.parse_series('6639'))

# with open('data.txt', 'w') as f:
#     f.write(str(get_riot_game(
#         'https://matchhistory.euw.leagueoflegends.com/de/#match-details/EUW1/4868679293',
#         # get_timeline=True,
#         add_names=True,
#         # patch="10.16"
#     )))
