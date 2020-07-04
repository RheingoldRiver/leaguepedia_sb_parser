from leaguepedia_sb_parser.parser import Parser
from river_mwclient.esports_client import EsportsClient
from river_mwclient.auth_credentials import AuthCredentials

credentials = AuthCredentials(user_file="me")
site = EsportsClient('lol', credentials=credentials)

sb_parser = Parser(site, 'LCK/2020 Season/Summer Season')

print(sb_parser.parse_riot_series(['https://matchhistory.na.leagueoflegends.com/en/#match-details/ESPORTSTMNT01/1415112?gameHash=bb66036323278a5c&tab=overview', 'https://matchhistory.na.leagueoflegends.com/en/#match-details/ESPORTSTMNT01/1415168?gameHash=552fc6b68f1c6847&tab=overview']))
