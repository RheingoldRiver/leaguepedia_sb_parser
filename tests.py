import lol_esports_parser

from leaguepedia_sb_parser.bayes_parser import BayesParser
from leaguepedia_sb_parser.riot_parser import RiotParser
from leaguepedia_sb_parser.live_parser import LiveParser
from leaguepedia_sb_parser.chinese_parser import ChineseParser
from leaguepedia_sb_parser.multi_series_parser import MultiParser
from mwrogue.esports_client import EsportsClient
from mwcleric.auth_credentials import AuthCredentials
from lol_esports_parser import get_riot_game
from lol_esports_parser import get_wp_series
import logging

credentials = AuthCredentials(user_file="me")
site = EsportsClient('lol', credentials=credentials)

riot_parser = RiotParser(site, 'LCS Proving Grounds/2021 Season/Summer/Proving Grounds Qualifiers')
# print(riot_parser.parse_series([
#     'https://matchhistory.na.leagueoflegends.com/en/#match-details/NA1/3981388323/46735781?tab=overview'
# ]))
#
# multi_parser = MultiParser(riot_parser)
#
# multi_parser.parse_multi_series('https://matchhistory.na.leagueoflegends.com/en/#match-details/ESPORTSTMNT01/1423603?gameHash=c67872b8e8b05e51&tab=overview\nhttps://matchhistory.na.leagueoflegends.com/en/#match-details/ESPORTSTMNT01/1423603?gameHash=c67872b8e8b05e51&tab=overview')

# print('<br>'.join(riot_parser.warnings))


# chinese_parser = ChineseParser(site, event='LPL 2021 Summer Playoffs', patch='11.1')
# print(chinese_parser.parse_series('8098'))

# with open('data.txt', 'w') as f:
#     f.write(str(get_riot_game(
#         'https://matchhistory.na.leagueoflegends.com/en/#match-details/ESPORTSTMNT02/1611575?gameHash=7cfc8b40c5243474&tab=overview',
#         # get_timeline=True,
#         patch="10.16"
#     )))

live_parser = LiveParser(site, 'Philly Esports Collegiate League of Legends Tournament')
print(live_parser.parse_series(['NA1_4119150232']))


# bayes_parser = BayesParser(site, 'VCS/2021_Season/Winter_Season')
# print(bayes_parser.parse_series(["ESPORTSTMNT01_2591840"]))
