import math
from typing import List

from lol_dto.names_helper.name_classes import ItemNameClass
from mwrogue.errors import InvalidEventError
from mwrogue.esports_client import EsportsClient
from mwrogue.wiki_time_parser import time_from_str
from lol_dto.classes.game import LolGame, LolGameTeam, LolGamePlayerSnapshot, LolGamePlayer, LolGamePlayerRune
import lol_id_tools

from leaguepedia_sb_parser.errors import EventCannotBeLocated


class Parser(object):
    HEADER_TEXT = "{{{{Scoreboard/Header|{}|{}}}}}"

    GAME_TEXT = '{{{{Scoreboard/Season 8{}\n{}\n}}}}'

    TEAM_KEYS = {'team1': 0, 'team2': 1}

    # team args, team bans, player args
    TEAM_TEXT = '{}{}\n{}'

    # |{blue}{1}={args}{items}{runes}
    PLAYER_TEXT = '|{}{}={{{{Scoreboard/Player{}{}{}}}}}'

    RUNES_TEXT = '\n|runes={{{{Scoreboard/Player/Runes|{}}}}}'

    MAX_BANS = 5

    TEAM_NAMES = ['blue', 'red']

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

        self.first_teams = None

    def save_teams(self, team1, team2):
        self.teams = [team1, team2]
        if self.first_teams is None:
            self.first_teams = [team1, team2]

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
        blue = self.get_initial_team_name(game.teams.BLUE)
        red = self.get_initial_team_name(game.teams.RED)
        if blue is None or red is None:
            if url is not None:
                self.determine_teams_from_wiki(url)
            else:
                self.save_teams(None, None)
            return
        self.save_teams(self.get_final_team_name(blue, 'blue') or blue,
                        self.get_final_team_name(red, 'red') or red
                        )

    def get_initial_team_name(self, team):
        ...

    def get_final_team_name(self, team_name, team_key):
        try:
            result = self.site.cache.get_team_from_event_tricode(self.event, team_name)
        except InvalidEventError:
            raise EventCannotBeLocated
        if result is None:
            # could be None either (a) because cannot find the team name
            # or (b) because it's live server and actually the original name is None and then gg us
            self.warnings.append(
                'Final team name for {} is missing (original: `{}`) - maybe you have to set |short= in TeamRoster if the \
                 code differs from what we use in Teamnames. You may also need to RefreshTeamnames or blank edit \
                the team page. Inferred event: {}'.format(
                    team_key, team_name, self.event
                )
            )
        return result

    def determine_teams_from_wiki(self, url):
        self.save_teams(None, None)

    def make_match_header(self):
        return self.HEADER_TEXT.format(self.teams[0] or '', self.teams[1] or '')

    def parse_one_game(self, game: LolGame, url, key: str = "statslink"):
        self.init_lol_id_tools()
        return self.GAME_TEXT.format(
            self.concat_args(self.extract_game_args(game, url, key=key)),
            self.parse_teams(game)
        )

    @staticmethod
    def init_lol_id_tools():
        """Deal with the race condition"""
        lol_id_tools.get_name(85, object_type="champion")

    def extract_game_args(self, game: LolGame, url, key):
        timestamp = time_from_str(game.start)
        patch = game.patch
        if self.patch is not None and patch is not None:
            patch = self.get_resolved_patch(patch)
        if self.patch is None and patch is None:
            self.warnings.append('Patch is not provided and also not available in game! Leaving blank....')
        game_args = [
            {'tournament': self.tournament},
            {'patch': patch or self.patch},
            {'winner': 1 if game.winner == 'BLUE' else 2},
            {'gamelength': self.get_duration(game.duration)},
            {'timezone': 'CET'},
            {'date': timestamp.cet_date},
            {'dst': timestamp.dst},
            {'time': timestamp.cet_time},
            {key: url},
            {'vodlink': ''},
            {'checksum': self.get_checksum(game)},
        ]
        return game_args

    def get_checksum(self, game: LolGame):
        ...

    def get_resolved_patch(self, patch):
        if self.patch != patch:
            self.warnings.append(
                'MatchSchedule patch doesn\'t match actual (match history) patch!! MS: {}, ingame {}. We used mh but please fix the wiki!'.format(
                    self.patch, patch))
        return patch

    @staticmethod
    def get_duration(duration):
        if duration is None:
            return None

        # this is how we'd do it if we wanted HH:MM:SS
        # return time.strftime('%H:%M:%S', time.gmtime(duration)).replace('00:', '')

        # but actually we need MM:SS no matter if there were a total number of hours or not
        return '{}:{}'.format(str(math.floor(duration / 60)), str(round(duration % 60, 2)).zfill(2))

    def parse_teams(self, game: LolGame):
        ret = []
        for i, team in enumerate(game.teams):
            team_key = 'team{}'.format(str(i + 1))
            ret.append(self.TEAM_TEXT.format(
                self.concat_args(self.extract_team_args(team, team_key)),
                self.list_args(
                    team.bansNames,
                    '{}ban'.format(team_key),
                    expected_len=self.MAX_BANS
                ),
                self.parse_players(self.TEAM_NAMES[i], team)
            ))
        return '\n'.join(ret)

    def extract_team_args(self, team: LolGameTeam, team_key):
        team_args = [
            {team_key + '': self.teams[self.TEAM_KEYS[team_key]]},
            {team_key + 'g': sum(int(player.endOfGameStats.gold) for player in team.players)},
            {team_key + 'k': sum(int(player.endOfGameStats.kills) for player in team.players)},
            {team_key + 'd': team.endOfGameStats.dragonKills},
            {team_key + 'b': team.endOfGameStats.baronKills},
            {team_key + 't': team.endOfGameStats.turretKills},
            {team_key + 'rh': team.endOfGameStats.riftHeraldKills},
            {team_key + 'i': team.endOfGameStats.inhibitorKills},
            {team_key + 'cloud': self.team_drake_count(team, "CLOUD")},
            {team_key + 'infernal': self.team_drake_count(team, "INFERNAL")},
            {team_key + 'mountain': self.team_drake_count(team, "MOUNTAIN")},
            {team_key + 'ocean': self.team_drake_count(team, "OCEAN")},
            {team_key + 'elder': self.team_drake_count(team, "ELDER")},
        ]
        return team_args

    @staticmethod
    def team_drake_count(team: LolGameTeam, dragon_type):
        if not hasattr(team, 'epicMonstersKills'):
            return None
        return len([_ for _ in team.epicMonstersKills if _.subType == dragon_type and _.type == 'DRAGON'])

    def parse_players(self, side_name, team: LolGameTeam):
        ret = []
        for i in range(5):
            player = team.players[i]
            ret.append(self.PLAYER_TEXT.format(
                side_name,
                str(i + 1),
                self.concat_args(self.extract_player_args(player, team)),
                self.list_args(
                    # don't include the last item because that's actually the trinket
                    [self.get_item_name(item) for item in team.players[i].endOfGameStats.items[:-1]],
                    'item'
                ),
                self.RUNES_TEXT.format(
                    ','.join([_.name if _.name is not None else str(_.id) for _ in player.runes])
                ) if self.should_get_rune_names(player) else ''
            ))
        return '\n'.join(ret)

    @staticmethod
    def get_item_name(item: ItemNameClass):
        if item.id == 0:
            return ''
        if item.name:
            return item.name.replace('%i:ornnIcon%', '')
        return item.id

    def extract_player_args(self, player: LolGamePlayer, team: LolGameTeam):
        player_name = self.get_player_ingame_name(player.inGameName, self.get_initial_team_name(team))
        if player.inGameName is not None and player_name is None or player_name == '':
            self.warnings.append('Player name cannot be parsed, using full name of {}'.format(player.inGameName))
            player_name = player.inGameName
        disambiguated_name = self.disambiguate_player_name(player_name, team)
        player_args = [
            {'link': disambiguated_name},
            {'champion': player.championName},
            {'kills': player.endOfGameStats.kills},
            {'deaths': player.endOfGameStats.deaths},
            {'assists': player.endOfGameStats.assists},
            {'gold': player.endOfGameStats.gold},
            {'cs': player.endOfGameStats.cs},
            {'visionscore': player.endOfGameStats.visionScore},
            {'damagetochamps': player.endOfGameStats.totalDamageDealtToChampions},
            {'summonerspell1': player.summonerSpells[0].name},
            {'summonerspell2': player.summonerSpells[1].name},
            {'keystone': player.runes[0].name if self.should_get_rune_names(player) else None},
            {'primary': player.primaryRuneTreeName if self.should_get_rune_names(player) else None},
            {'secondary': player.secondaryRuneTreeName if self.should_get_rune_names(player) else None},
            {'trinket': player.endOfGameStats.items[6].name},

            # keep this last so it's consecutive with pentakillvod
            {'pentakills': player.endOfGameStats.pentaKills},
        ]
        if player.endOfGameStats.pentaKills or 0 > 0:
            player_args.append({'pentakillvod': ''})
        return player_args

    def get_player_ingame_name(self, ingame_name, team_name):
        pass

    def disambiguate_player_name(self, player_name, team: LolGameTeam):
        if player_name is None:
            return None
        result = self.site.cache.get_disambiguated_player_from_event(
            self.event,
            self.site.cache.get_team_from_event_tricode(self.event, self.get_initial_team_name(team)),
            player_name
        )
        if result is not None:
            return result
        warning = 'Disambiguated name for {} couldn\'t be found, perhaps player is missing from participants!'
        self.warnings.append(warning.format(player_name))
        return player_name

    @staticmethod
    def should_get_rune_names(player: LolGamePlayer):
        if not hasattr(player, 'runes'):
            return False
        runes = player.runes
        if runes is None:
            return False
        if any([rune is None for rune in runes]):
            return False
        if any([rune.id is None for rune in runes]):
            return False
        return True
