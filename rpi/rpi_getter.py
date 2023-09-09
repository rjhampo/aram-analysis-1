import subprocess, tenacity, aiohttp, aiolimiter, gzip, asyncio, arrow, random, os, json, dotenv, board, digitalio, adafruit_character_lcd.character_lcd as characterlcd
import current_model
import sqlalchemy.ext.asyncio as sqlaio
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime

dotenv.load_dotenv()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com",
    "X-Riot-Token": os.environ.get('RIOT_API_KEY')
}

patch_date_range = {'start':arrow.get(2023, 8, 3, 0,0,0).int_timestamp, 'end':arrow.get(2023, 8, 16, 0,0,0).int_timestamp} # Patch 13.15

lcd_rs = digitalio.DigitalInOut(board.D22)
lcd_en = digitalio.DigitalInOut(board.D17)
lcd_d4 = digitalio.DigitalInOut(board.D25)
lcd_d5 = digitalio.DigitalInOut(board.D24)
lcd_d6 = digitalio.DigitalInOut(board.D23)
lcd_d7 = digitalio.DigitalInOut(board.D18)

lcd = characterlcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, 16, 2)

class AsyncDataExtract:
    def __init__(self, headers, seed, num_dp, patch_date, async_engine_obj):
        self.limiter = aiolimiter.AsyncLimiter(max_rate=1, time_period=1.2)
        self.session = sqlaio.async_sessionmaker(async_engine_obj)
        self.headers = headers
        self.data_counter = 0
        self.num_dp = num_dp
        self.patch_date = patch_date
        self.seed_players = [seed]
        self.done_players = set()
        self.done_matches = set()
        self.run_duration = 0
        self.start_time = None

    def no_connection_warning(self, err):
        print(err)
        lcd.message = f"! C:{self.data_counter}\nDUR:{self.run_duration}"

    def process_match(self, match_response):
        data = match_response['info']
        return {'matchId': match_response['metadata'].get('matchId'), 'gameEndTimestamp': datetime.fromtimestamp(data.get('gameEndTimestamp')/1000),
                'gameStartTimestamp': datetime.fromtimestamp(data.get('gameStartTimestamp')/1000), 'gameType': data.get('gameType'), 'queueId': data.get('queueId'),
                'gameVersion': data.get('gameVersion'), 'gameEndedInEarlySurrender': data['participants'][0].get('gameEndedInEarlySurrender'),
                'gameEndedInSurrender': data['participants'][0].get('gameEndedInSurrender')}

    def process_team(self, match_response, team_response, participant_response):
        return {'teamId': match_response['metadata'].get('matchId') + str(team_response['teamId']), 'matchId': match_response['metadata'].get('matchId'),
                'team': team_response['teamId'], 'win': team_response['win'], 'bans': team_response['bans'], 'baronFirst': team_response['objectives']['baron']['first'], 
                'champFirst': team_response['objectives']['champion']['first'], 'dragonFirst': team_response['objectives']['dragon']['first'], 
                'inhibFirst': team_response['objectives']['inhibitor']['first'], 'riftheraldFirst': team_response['objectives']['riftHerald']['first'], 
                'towerFirst': team_response['objectives']['tower']['first'], 'baronKills': team_response['objectives']['baron']['kills'], 
                'champKills': team_response['objectives']['champion']['kills'], 'dragonKills': team_response['objectives']['dragon']['kills'], 
                'inhibKills': team_response['objectives']['inhibitor']['kills'], 'riftheraldKills': team_response['objectives']['riftHerald']['first'],
                'towerKills': team_response['objectives']['tower']['first'], 'turretsLost': participant_response['turretsLost'], 
                'inhibitorsLost': participant_response['inhibitorsLost'], 'teamEarlySurrendered': participant_response['teamEarlySurrendered'], 
                'gameEndedInSurrender': participant_response['gameEndedInSurrender']}

    def process_participant(self, match_response, team_response, participant_response):
        processed_response = participant_response
        processed_response['puuidTeamId'] = match_response['metadata'].get('matchId') + str(team_response['teamId']) + participant_response['puuid']
        processed_response['teamId'] = match_response['metadata'].get('matchId') + str(team_response['teamId'])
        processed_response['defensePerk'] = participant_response['perks']['statPerks']['defense']
        processed_response['flexPerk'] = participant_response['perks']['statPerks']['flex']
        processed_response['offensePerk'] = participant_response['perks']['statPerks']['offense']
        processed_response['primaryStylePerk'] = participant_response['perks']['styles'][0]
        processed_response['secondaryStylePerk'] = participant_response['perks']['styles'][1]
        return processed_response

    async def get_matches(self, seed_player, client):
        async for attempt in tenacity.AsyncRetrying(wait=tenacity.wait_fixed(10), retry=tenacity.retry_if_exception_type((aiohttp.ClientConnectorError, aiohttp.ClientOSError, aiohttp.ClientResponseError)), after=self.no_connection_warning):
            with attempt:
                async with self.limiter:
                    response = await client.get(f'https://sea.api.riotgames.com/lol/match/v5/matches/by-puuid/{seed_player}/ids?startTime={self.patch_date["start"]}&endTime={self.patch_date["end"]}&queue=450&start=0&count=100')
                    response_json = await response.json()
                if ('status' in response_json) and (response_json['status']['status_code'] == 429):
                    raise aiohttp.ClientResponseError(request_info=response.request_info, history=response.history, status=429)
            if not attempt.retry_state.outcome.failed:
                attempt.retry_state.set_result(response_json)
        return response_json

    async def get_match(self, seed_match, client):
        async for attempt in tenacity.AsyncRetrying(wait=tenacity.wait_fixed(10), retry=tenacity.retry_if_exception_type((aiohttp.ClientConnectorError, aiohttp.ClientOSError, aiohttp.ClientResponseError)), after=self.no_connection_warning):
            with attempt:
                async with self.limiter:
                    response = await client.get(f'https://sea.api.riotgames.com/lol/match/v5/matches/{seed_match}')
                    response_json = await response.json()
                if ('status' in response_json) and (response_json['status']['status_code'] == 429):
                    raise aiohttp.ClientResponseError(request_info=response.request_info, history=response.history, status=429)
            if not attempt.retry_state.outcome.failed:
                attempt.retry_state.set_result(response_json)
        return response_json

    async def write_to_db(self, table, data):
        async with self.session() as session:
            await session.execute(insert(table).on_conflict_do_nothing(), data)
            await session.commit()

    async def gather_matches(self):
        participant_tables = [current_model.ParticipantCombat, current_model.ParticipantObjective,
                        current_model.ParticipantVision, current_model.ParticipantSupport, current_model.ParticipantSpellCast,
                        current_model.ParticipantEquipPerk, current_model.ParticipantShopTX]
        lcd.clear()
        self.start_time = datetime.now()
        
        async with aiohttp.ClientSession(headers=self.headers) as client:
            while self.data_counter < self.num_dp:
                seed_player = random.choice(self.seed_players)
                self.seed_players.remove(seed_player)
                # if seed_player not in self.done_players:
                matchlist_response = await self.get_matches(seed_player, client)
                self.done_players.add(seed_player)
                    
                if not matchlist_response: continue
                match_tasks = [self.get_match(seed_match, client) for seed_match in matchlist_response if seed_match not in self.done_matches]
                if not match_tasks: continue
                matches_json = await asyncio.gather(*match_tasks)

                for seed_match_json in matches_json:
                    if 'metadata' in seed_match_json:    # Makes sure no invalid responses get processed
                        for participant in seed_match_json['metadata']['participants']:
                            if (participant not in self.done_players) and (participant not in self.seed_players):
                                self.seed_players.append(participant)
                        match_input = self.process_match(seed_match_json)
                        await self.write_to_db(current_model.Match, match_input)
                        team_input = []
                        for i, team in enumerate(seed_match_json['info']['teams']):
                            sample_participant = seed_match_json['info']['participants'][i*5]
                            team_input.append(self.process_team(seed_match_json, team, sample_participant))
                        await self.write_to_db(current_model.Team, team_input)
                        participant_input = []
                        for i, participant in enumerate(seed_match_json['info']['participants']):
                            participant_input.append(self.process_participant(seed_match_json, seed_match_json['info']['teams'][(i//5) % 2], participant))
                        async with self.session() as session:
                            await session.execute(insert(current_model.Participant).on_conflict_do_nothing(), participant_input)
                            await session.commit()
                        participant_write_tasks = [self.write_to_db(table, participant_input) for table in participant_tables]
                        await asyncio.gather(*participant_write_tasks)
                        
                        self.done_matches.add(seed_match_json['metadata']['matchId'])

                    self.data_counter = len(self.done_matches)
                    self.run_duration = (datetime.now() - self.start_time).total_seconds()
                    mem_list = subprocess.run('free', capture_output=True, text=True).stdout.split()
                    mem_usage = (int(mem_list[8])/int(mem_list[7]))*100
                    lcd.clear()
                    lcd.message = f"C:{self.data_counter} M:{mem_usage:.0f}%\nD:{self.run_duration:.0f}"

async_engine = sqlaio.create_async_engine(os.environ.get('SERVER_URL'), echo = True)

extractor = AsyncDataExtract(headers=headers, seed='nyJFMam4RF-ZUtMbQ3_SBpyAqfbTWOHGfqqBzu3YeaJDpIjkQ4g9t_HtUVslrqBfrkVZsuYVi0vcvw',
                               num_dp=1000000, patch_date=patch_date_range, async_engine_obj=async_engine)

try:
    asyncio.run(extractor.gather_matches())
except Exception as e:
    print(str(e))
    lcd.clear()
    lcd.message = "ERROR"
