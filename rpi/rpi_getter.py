import tenacity, aiohttp, aiolimiter, gzip, asyncio, arrow, random, os, json, dotenv



patch_date_range = {'start':arrow.get(2023, 6, 1, 0,0,0).int_timestamp, 'end':arrow.get(2023, 6, 14, 0,0,0).int_timestamp} # Patch 13.11

class AsyncDataExtract3:
    def __init__(self, headers, seed, num_dp, patch_date, file_name):
        self.limiter = aiolimiter.AsyncLimiter(max_rate=1, time_period=1.2)
        self.headers = headers
        self.data_counter = 0
        self.num_dp = num_dp
        self.patch_date = patch_date
        self.seed_players = [seed]
        self.done_players = set()
        self.done_matches = set()
        self.file_name = file_name
        
    def __del__(self):
        self.client.close()
    
    def flatten(self, to_flatten, level):
        match level:
            case 2:
                return [x for xs in to_flatten for x in xs]
            case 3:
                return [x for xs in to_flatten for xs2 in xs for x in xs2]
    
    def extract_players(self, seed_match_json):
        return [player for player in seed_match_json['metadata']['participants']]
    
    def no_connection_warning(self, err):
        print('No connection or exceeded requests!')
    
    async def get_matches(self, seed_player):
        async for attempt in tenacity.AsyncRetrying(wait=tenacity.wait_fixed(10000), retry=tenacity.retry_if_exception_type((aiohttp.ClientConnectorError, aiohttp.ClientOSError, aiohttp.ClientResponseError)), after=self.no_connection_warning):
            with attempt:
                async with self.limiter:
                    response = await self.client.get(f'https://sea.api.riotgames.com/lol/match/v5/matches/by-puuid/{seed_player}/ids?startTime={self.patch_date["start"]}&endTime={self.patch_date["end"]}&queue=450&start=0&count=100')
                    response_json = await response.json()
                if ('status' in response_json) and (response_json['status']['status_code'] == 429):
                    raise aiohttp.ClientResponseError(request_info=response.request_info, history=response.history, status=429)
            if not attempt.retry_state.outcome.failed:
                attempt.retry_state.set_result(response_json)
        return response_json

    async def get_match(self, seed_match):
        async for attempt in tenacity.AsyncRetrying(wait=tenacity.wait_fixed(10000), retry=tenacity.retry_if_exception_type((aiohttp.ClientConnectorError, aiohttp.ClientOSError, aiohttp.ClientResponseError)), after=self.no_connection_warning):
            with attempt:
                async with self.limiter:
                    response = await self.client.get(f'https://sea.api.riotgames.com/lol/match/v5/matches/{seed_match}')
                    response_json = await response.json()
                if ('status' in response_json) and (response_json['status']['status_code'] == 429):
                    raise aiohttp.ClientResponseError(request_info=response.request_info, history=response.history, status=429)
            if not attempt.retry_state.outcome.failed:
                attempt.retry_state.set_result(response_json)
        return response_json
    
    async def gather_matches(self):
        with (gzip.open(f'{self.file_name}.jsonl.gz', mode='ab') as out_file, aiohttp.ClientSession(headers=self.headers) as client):
            out_file.write('['.encode('utf-8'))
            while self.data_counter < self.num_dp:
                seed_player = random.choice(self.seed_players)
                self.seed_players.remove(seed_player)
                if seed_player not in self.done_players:
                    matchlist_response = await self.get_matches(seed_player)
                    self.done_players.add(seed_player)
                    
                    if not matchlist_response: continue
                    match_tasks = [self.get_match(seed_match) for seed_match in matchlist_response if seed_match not in self.done_matches]
                    if not match_tasks: continue
                    matches_json = await asyncio.gather(*match_tasks)

                    for seed_match_json in matches_json:
                        if 'metadata' in seed_match_json:
                            for participant in seed_match_json['metadata']['participants']:
                                if participant not in self.done_players:
                                    self.seed_players.append(participant)
                                    
                            json_buffer = json.dumps(seed_match_json) + ','
                            out_file.write(json_buffer.encode('utf-8'))
                            self.done_matches.add(seed_match_json['metadata']['matchId'])

                    self.data_counter = len(self.done_matches)
                    print(self.data_counter)
            
            out_file.write('{"a":1}]'.encode('utf-8'))
            
        await self.client.close()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com",
    "X-Riot-Token": os.environ.get('RIOT_API_KEY')
}

extractor4 = AsyncDataExtract3(headers=headers, seed='rnSanmBvzma5coD59loD39if9nkV3Yo28i4ool_8Sa83m38n-EGDzt1qGUCs33lPxA1dvuyGCwBWRA',
                               num_dp=20, patch_date=patch_date_range, file_name='test6')

asyncio.run(extractor4.gather_matches())