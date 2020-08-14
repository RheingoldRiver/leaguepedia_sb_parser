import time
from river_mwclient.esports_client import EsportsClient
from river_mwclient.wiki_time_parser import time_from_str
from lol_dto.classes.game import LolGame


class Parser(object):
    HEADER_TEXT = "{{{{MatchRecapS8/Header|{}|{}}}}}"
    
    GAME_TEXT = '{{{{MatchRecapS8{}\n{}}}}}'
    
    TEAM_KEYS = {'team1': 0, 'team2': 1}
    
    # team args, team bans, player args
    TEAM_TEXT = '{}{}\n{}'
    
    # |{blue}{1}={args}{items}{runes}
    PLAYER_TEXT = '|{}{}={{{{MatchRecapS8/Player{}{}{}}}}}'
    
    RUNES_TEXT = '\n|runes={{{{Scoreboard/Player/Runes|{}}}}}'
    
    MAX_BANS = 5
    
    def __init__(self, site: EsportsClient, event: str, patch: str = None):
        # patch could be an empty string if it's from a cookie
        # handle it here because there's branching changes in flask
        if patch == '':
            patch = None
        self.site = site
        self.patch = patch
        self.tournament = event
        self.event = site.target(event)
        self.warnings = []
        
        # this is the only case of a thing we need to keep track of separate from just generating the sb string
        # it has to be used to generate the heading
        # so even though this really doesn't belong here let's just, allow it ok sorry
        self.teams = []
    
    def clear_warnings(self):
        self.warnings = []
    
    def parse_series(self, urls: list, include_header=True):
        pass
    
    def parse_game(self, url):
        pass
    
    @staticmethod
    def concat_args(lookup: list):
        ret = ''
        for pair in lookup:
            pair: dict
            for key in pair.keys():
                if pair[key] is None:
                    ret = ret + '|{}= '.format(key)
                else:
                    ret = ret + '|{}= {} '.format(key, str(pair[key]))
        return ret
    
    @staticmethod
    def list_args(args: list, param_prefix: str, expected_len=None):
        if args is None:
            if expected_len is None:
                return None
            ret = ''
            for i in range(expected_len):
                ret = ret + '|{}{}= '.format(param_prefix, str(i + 1))
            return ret
        ret = ''
        for i, arg in enumerate(args):
            ret = ret + '|{}{}= {}'.format(param_prefix, str(i + 1), arg)
        return ret

    def populate_teams(self, game: LolGame, url=None):
        blue = game['teams']['BLUE'].get('name')
        red = game['teams']['RED'].get('name')
        if blue is None or red is None:
            if url is not None:
                self.determine_teams_from_wiki(url)
            else:
                self.teams = [None, None]
            return
        self.teams = [
            self.get_final_team_name(blue, 'blue') or blue,
            self.get_final_team_name(red, 'red') or red,
        ]
    
    def get_final_team_name(self, team_name, team_key):
        result = self.site.cache.get_team_from_event_tricode(self.event, team_name)
        if result is None:
            # could be None either (a) because cannot find the team name
            # or (b) because it's live server and actually the original name is None and then gg us
            self.warnings.append(
                'Final team name for {} is missing (original: {})'.format(
                    team_key, team_name
                )
            )
        return result
    
    def determine_teams_from_wiki(self, url):
        self.teams = [None, None]
    
    def make_match_header(self):
        return self.HEADER_TEXT.format(self.teams[0] or '', self.teams[1] or '')
    
    def parse_one_game(self, game: LolGame, url):
        return self.GAME_TEXT.format(
            self.concat_args(self.extract_game_args(game, url)),
            self.parse_teams(game)
        )
    
    def extract_game_args(self, game, url):
        timestamp = time_from_str(game['start'])
        patch = game.get('patch')
        if self.patch is not None and patch is not None:
            patch = self.get_resolved_patch(patch)
        if self.patch is None and patch is None:
            self.warnings.append('Patch is not provided and also not available in game! Leaving blank....')
        game_args = [
            {'tournament': self.tournament},
            {'patch': patch or self.patch},
            {'winner': 1 if game['winner'] == 'BLUE' else 2},
            {'gamelength': self.get_duration(game['duration']) if 'duration' in game else None},
            {'timezone': 'CET'},
            {'date': timestamp.cet_date},
            {'dst': timestamp.dst},
            {'time': timestamp.cet_time},
            {'statslink': url},
            {'vodlink': ''},
        ]
        return game_args
    
    def get_resolved_patch(self, patch):
        if self.patch != patch:
            self.warnings.append('Provided patch doesn\'t match ingame patch!! Provided: {}, ingame {}. We used provided.'.format(self.patch, patch))
        return patch
    
    @staticmethod
    def get_duration(duration):
        if duration is None:
            return None
        # format hh:mm:ss and then strip leading 0's for games under 1 hour (aka most games)
        return time.strftime('%H:%M:%S', time.gmtime(duration)).replace('00:', '')
    
    def parse_teams(self, game):
        ret = []
        for i, team in enumerate(game['teams']):
            team_key = 'team{}'.format(str(i + 1))
            ret.append(self.TEAM_TEXT.format(
                self.concat_args(self.extract_team_args(game['teams'][team], team_key)),
                self.list_args(
                    game['teams'][team].get('bansNames'),
                    '{}ban'.format(team_key),
                    expected_len=self.MAX_BANS
                ),
                self.parse_players(team.lower(), game['teams'][team])
            ))
        return '\n'.join(ret)
    
    def extract_team_args(self, team, team_key):
        team_args = [
            {team_key + '': self.teams[self.TEAM_KEYS[team_key]]},
            {team_key + 'g': sum(player['endOfGameStats']['gold'] for player in team['players'])},
            {team_key + 'k': sum(player['endOfGameStats']['kills'] for player in team['players'])},
            {team_key + 'd': team['endOfGameStats'].get('dragonKills')},
            {team_key + 'b': team['endOfGameStats'].get('baronKills')},
            {team_key + 't': team['endOfGameStats'].get('towerKills')},
            {team_key + 'rh': team['endOfGameStats'].get('riftHeraldKills')},
            {team_key + 'i': team['endOfGameStats'].get('inhibitorKills')},
            {team_key + 'cloud': self.team_drake_count(team, "CLOUD")},
            {team_key + 'infernal': self.team_drake_count(team, "INFERNAL")},
            {team_key + 'mountain': self.team_drake_count(team, "MOUNTAIN")},
            {team_key + 'ocean': self.team_drake_count(team, "OCEAN")},
            {team_key + 'elder': self.team_drake_count(team, "ELDER")},
        ]
        return team_args
    
    @staticmethod
    def team_drake_count(team, dragon_type):
        if 'monstersKills' not in team:
            return None
        return len([_ for _ in team["monstersKills"] if _.get("subType") == dragon_type])
    
    def parse_players(self, side_name, team):
        ret = []
        for i in range(5):
            player = team['players'][i]
            ret.append(self.PLAYER_TEXT.format(
                side_name,
                str(i + 1),
                self.concat_args(self.extract_player_args(player, team)),
                self.list_args(
                    # don't include the last item because that's actually the trinket
                    [item['name'] for item in team['players'][i]['endOfGameStats']['items'][:-1]],
                    'item'
                ),
                self.RUNES_TEXT.format(
                    ','.join([_.get('name') for _ in player['runes']])
                ) if 'runes' in player else ''
            ))
        return '\n'.join(ret)
    
    def extract_player_args(self, player, team):
        player_name = self.get_player_ingame_name(player.get('inGameName'), team.get('name'))
        if player.get('inGameName') is not None and player_name is None or player_name == '':
            self.warnings.append('Player name cannot be parsed, using full name of {}'.format(player.get('inGameName')))
            player_name = player.get('inGameName')
        disambiguated_name = self.disambiguate_player_name(player_name, team)
        player_args = [
            {'link': disambiguated_name},
            {'champion': player['championName']},
            {'kills': player['endOfGameStats']['kills']},
            {'deaths': player['endOfGameStats']['deaths']},
            {'assists': player['endOfGameStats']['assists']},
            {'gold': player['endOfGameStats']['gold']},
            {'cs': player['endOfGameStats']['cs']},
            {'visionscore': player['endOfGameStats'].get('visionScore')},
            {'damagetochamps': player['endOfGameStats'].get('totalDamageDealtToChampions')},
            {'summonerspell1': player['summonerSpells'][0]['name']},
            {'summonerspell2': player['summonerSpells'][1]['name']},
            {'keystone': player['runes'][0]['name'] if 'runes' in player else None},
            {'secondary': player.get('secondaryRuneTreeName')},
            {'trinket': player['endOfGameStats']['items'][6]['name']},
            
            # keep this last so it's consecutive with pentakillvod
            {'pentakills': player['endOfGameStats'].get('pentaKills')},
        ]
        if 'pentaKills' in player['endOfGameStats'] and player['endOfGameStats']['pentaKills'] > 0:
            player_args.append({'pentakillvod': ''})
        return player_args
    
    def get_player_ingame_name(self, ingame_name, team_name):
        pass
    
    def disambiguate_player_name(self, player_name, team):
        if player_name is None:
            return None
        result = self.site.cache.get_disambiguated_player_from_event(
            self.event,
            self.site.cache.get_team_from_event_tricode(self.event, team.get('name')),
            player_name
        )
        if result is not None:
            return result
        warning = 'Disambiguated name for {} couldn\'t be found, perhaps player is missing from participants!'
        self.warnings.append(warning.format(player_name))
        return player_name
