# -*- coding: utf-8 -*-
"""
Created on Sat Jun 24 15:26:47 2023

@author: James Ampo
"""

import riotwatcher as rw
import dotenv
import os
import arrow
import aiolimiter
import asyncio
import jsonlines
import nest_asyncio
from collections.abc import Iterable

nest_asyncio.apply()
dotenv.load_dotenv()
lol_watcher = rw.LolWatcher(os.environ.get("RIOT_API_KEY"))
patch_date_range = {'start':arrow.get(2023, 6, 1, 0,0,0).int_timestamp, 'end':arrow.get(2023, 6, 14, 0,0,0).int_timestamp} # Patch 13.11
seed_player = lol_watcher.summoner.by_puuid(encrypted_puuid="uRZ9d8VNRDsYFDtlTy3Cr9VTa3rFN3Y504Woem4uyYdCGWZsw2uKF9OoX3DbiseOXOuq7dajnxamtw", region="PH2")

class DataExtract:
    def __init__(self, seed, num_dp, patch_date, file_name):
        self.limiter = aiolimiter.AsyncLimiter(1, time_period=1.2)
        self.data_counter = 0
        self.num_dp = num_dp
        self.patch_date = patch_date
        self.seed_players = [seed]
        self.done_players = set()
        self.matches_id = []
        self.done_matches = set()
        self.matches_json = []
        self.file_name = file_name
        with jsonlines.open(f'{self.file_name}.ndjson', mode='w') as out:
            pass
    
    async def get_matches(self, seed_player):
        return lol_watcher.match.matchlist_by_puuid(puuid=seed_player, region="PH2", count=100, queue=450, start_time=self.patch_date['start'], end_time=self.patch_date['end'])

    async def get_match(self, seed_match):
        return lol_watcher.match.by_id(match_id=seed_match, region="PH2")

    async def get_player(self, seed_player):
        return lol_watcher.summoner.by_puuid(encrypted_puuid=seed_player, region="PH2")

    def extract_players(self, seed_match_json):
        return [player for player in seed_match_json['metadata']['participants']]
    
    def flatten(self, to_flatten, level):
        match level:
            case 2:
                return [x for xs in to_flatten for x in xs]
            case 3:
                return [x for xs in to_flatten for xs2 in xs for x in xs2]

    async def main(self):
        async with self.limiter:
            while self.data_counter < self.num_dp:
                matchlist_tasks = [self.get_matches(seed_player) for seed_player in self.seed_players if (seed_player not in self.done_players)]
                matchlist_response = await asyncio.gather(*matchlist_tasks)
                self.matches_id.append(matchlist_response)
                self.matches_id = self.flatten(self.matches_id, 3)

                for seed in self.seed_players:
                    self.done_players.add(seed)

                match_tasks = [self.get_match(seed_match) for seed_match in self.matches_id if (seed_match not in self.done_matches)]
                match_response = await asyncio.gather(*match_tasks)
                self.matches_json.append(match_response)
                self.matches_json = self.flatten(self.matches_json, 2)
                with jsonlines.open(f'{self.file_name}.ndjson', mode='a') as out:
                    for match in self.matches_json:
                        out.write(match)

                self.seed_players = [participant for seed_match_json in self.matches_json for participant in seed_match_json['metadata']['participants'] if seed_match_json['metadata']['matchId'] not in self.done_matches]

                for match in self.matches_id:
                    self.done_matches.add(match)
                self.matches_id = []
                self.matches_json = []

                self.data_counter += 1
                print(self.data_counter)

extractor1 = DataExtract(seed="uRZ9d8VNRDsYFDtlTy3Cr9VTa3rFN3Y504Woem4uyYdCGWZsw2uKF9OoX3DbiseOXOuq7dajnxamtw",
                         num_dp=200, patch_date=patch_date_range, file_name='test1')

asyncio.run(extractor1.main())