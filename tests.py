from leaguepedia_sb_parser.riot_parser import RiotParser
from leaguepedia_sb_parser.chinese_parser import ChineseParser
from river_mwclient.esports_client import EsportsClient
from river_mwclient.auth_credentials import AuthCredentials
from lol_esports_parser import get_riot_game
from lol_esports_parser import get_wp_series
from lol_esports_parser import get_qq_series

credentials = AuthCredentials(user_file="me")
site = EsportsClient('lol', credentials=credentials)

# riot_parser = RiotParser(site, 'GUL 2020 Closing Playoffs')
# print(riot_parser.parse_series(['https://matchhistory.euw.leagueoflegends.com/en/#match-details/EUW1/4740814349?tab=overview']))


# chinese_parser = ChineseParser(site, 'LPL/2020 Season/Summer Season', patch="10.15.1")
# print(chinese_parser.parse_series('6639'))

with open('data.txt', 'w') as f:
    f.write(str(get_qq_series(
        'https://lpl.qq.com/es/stats.shtml?bmid=6131',
        # get_timeline=True,
        add_names=True
    )))