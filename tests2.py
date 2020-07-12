from leaguepedia_sb_parser.riot_parser import RiotParser
from leaguepedia_sb_parser.chinese_parser import ChineseParser
from river_mwclient.esports_client import EsportsClient
from river_mwclient.auth_credentials import AuthCredentials
from leaguepedia_sb_parser.multi_series_parser import MultiParser

credentials = AuthCredentials(user_file="me")
site = EsportsClient('lol', credentials=credentials)

riot_parser = RiotParser(site, 'LCK/2020 Season/Summer Season')
chinese_parser = ChineseParser(site, 'LPL/2020 Season/Summer Season')
multi_parser = MultiParser(chinese_parser)

text = """6200"""

print(multi_parser.parse_multi_series(text))
