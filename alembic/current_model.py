from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import JSON, ARRAY, String, INTEGER, DECIMAL
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Match(Base):
    __tablename__ = "match"

    matchId: Mapped[str] = mapped_column(primary_key = True)
    gameEndTimestamp: Mapped[datetime]
    gameStartTimestamp: Mapped[datetime]
    gameType: Mapped[str]
    queueId: Mapped[int] = mapped_column(ForeignKey("gamemode.queueId"))
    gameVersion: Mapped[str]
    gameEndedInEarlySurrender: Mapped[bool]
    gameEndedInSurrender: Mapped[bool]

class Team(Base):
    __tablename__ = "team"

    teamId: Mapped[str] = mapped_column(primary_key = True)
    matchId = mapped_column(ForeignKey("match.matchId"))
    team: Mapped[int]
    win: Mapped[bool]
    bans = mapped_column(JSON, nullable = True)
    
    baronFirst: Mapped[bool]
    champFirst: Mapped[bool]
    dragonFirst: Mapped[bool]
    inhibFirst: Mapped[bool]
    riftheraldFirst: Mapped[bool]
    towerFirst: Mapped[bool]

    baronKills: Mapped[int]
    champKills: Mapped[int]
    dragonKills: Mapped[int]
    inhibKills: Mapped[int]
    riftheraldKills: Mapped[int]
    towerKills: Mapped[int]

    turretsLost: Mapped[int]
    inhibitorsLost: Mapped[int]
    teamEarlySurrendered: Mapped[bool]
    gameEndedInSurrender: Mapped[bool]

class Participant(Base):
    __tablename__ = "participant"

    puuidTeamId: Mapped[str] = mapped_column(primary_key = True)
    teamId = mapped_column(ForeignKey("team.teamId"))
    puuid: Mapped[str]
    item0: Mapped[int | None] = mapped_column(ForeignKey("shopitem.itemId"))
    item1: Mapped[int | None] = mapped_column(ForeignKey("shopitem.itemId"))
    item2: Mapped[int | None] = mapped_column(ForeignKey("shopitem.itemId"))
    item3: Mapped[int | None] = mapped_column(ForeignKey("shopitem.itemId"))
    item4: Mapped[int | None] = mapped_column(ForeignKey("shopitem.itemId"))
    item5: Mapped[int | None] = mapped_column(ForeignKey("shopitem.itemId"))
    item6: Mapped[int | None] = mapped_column(ForeignKey("shopitem.itemId"))
    teamPosition: Mapped[str | None]
    role: Mapped[str]
    lane: Mapped[str]
    kills: Mapped[int]
    deaths: Mapped[int]
    assists: Mapped[int]
    championId: Mapped[int] = mapped_column(ForeignKey("champion.championId"))
    champLevel: Mapped[int]
    championTransform: Mapped[int]
    challenges = mapped_column(JSON)

class ParticipantCombat(Base):
    __tablename__ = "combat"
    
    puuidTeamId = mapped_column(ForeignKey("participant.puuidTeamId"), primary_key = True)
    totalDamageTaken: Mapped[int]
    trueDamageTaken: Mapped[int]
    physicalDamageTaken: Mapped[int]
    magicDamageTaken: Mapped[int]
    damageSelfMitigated = Mapped[int]

    totalDamageDealt: Mapped[int]
    totalDamageDealtToChampions: Mapped[int]
    trueDamageDealt: Mapped[int]
    trueDamageDealtToChampions: Mapped[int]
    physicalDamageDealt: Mapped[int]
    physicalDamageDealtToChampions: Mapped[int]
    magicDamageDealt: Mapped[int]
    magicDamageDealtToChampions: Mapped[int]

    doubleKills: Mapped[int]
    tripleKills: Mapped[int]
    quadraKills: Mapped[int]
    pentaKills: Mapped[int]
    killingSprees: Mapped[int]
    largestMultiKill: Mapped[int]
    largestKillingSpree: Mapped[int]
    largestCriticalStrike: Mapped[int]
    firstBloodKill: Mapped[bool]
    firstBloodAssist: Mapped[bool]
    bountyLevel: Mapped[int]

class ParticipantObjective(Base):
    __tablename__ = "objective"
    
    puuidTeamId = mapped_column(ForeignKey("participant.puuidTeamId"), primary_key = True)
    damageDealtToTurrets: Mapped[int]
    damageDealtToObjectives: Mapped[int]
    damageDealtToBuildings: Mapped[int]

    turretTakedowns: Mapped[int]
    turretKills: Mapped[int]
    firstTowerAssist: Mapped[bool]
    firstTowerKill: Mapped[bool]
    nexusTakedowns: Mapped[int]
    nexusKills: Mapped[int]
    inhibitorTakedowns: Mapped[int]
    inhibitorKills: Mapped[int]

    totalMinionsKilled: Mapped[int]
    totalEnemyJungleMinionsKilled: Mapped[int]
    totalAllyJungleMinionsKilled: Mapped[int]
    neutralMinionsKilled: Mapped[int]

    dragonKills: Mapped[int]
    baronKills: Mapped[int]
    objectivesStolen: Mapped[int]
    objectivesStolenAssists: Mapped[int]

class ParticipantVision(Base):
    __tablename__ = "vision"

    puuidTeamId = mapped_column(ForeignKey("participant.puuidTeamId"), primary_key = True)
    visionScore: Mapped[int]
    visionWardsBoughtInGame: Mapped[int]
    wardsKilled: Mapped[int]
    wardsPlaced: Mapped[int]
    sightWardsBoughtInGame: Mapped[int]
    detectorWardsPlaced: Mapped[int]

class ParticipantSupport(Base):
    __tablename__ = "support"

    puuidTeamId = mapped_column(ForeignKey("participant.puuidTeamId"), primary_key = True)
    totalHeal: Mapped[int]
    totalUnitsHealed: Mapped[int]
    totalHealsOnTeammates: Mapped[int]
    totalDamageShieldedOnTeammates: Mapped[int]
    totalTimeCCDealt: Mapped[int]
    timeCCingOthers: Mapped[int]
    longestTimeSpentLiving: Mapped[int]
    totalTimeSpentDead: Mapped[int]

class ParticipantSpellCast(Base):
    __tablename__ = "spellcast"

    puuidTeamId = mapped_column(ForeignKey("participant.puuidTeamId"), primary_key = True)
    spell1Id: Mapped[int] = mapped_column(ForeignKey('spell.spellId'))
    spell1Casts: Mapped[int]
    spell2Id: Mapped[int] = mapped_column(ForeignKey('spell.spellId'))
    spell2Casts: Mapped[int]
    spell3Id: Mapped[int] = mapped_column(ForeignKey('spell.spellId'))
    spell3Casts: Mapped[int]
    spell4Id: Mapped[int] = mapped_column(ForeignKey('spell.spellId'))
    spell4Casts: Mapped[int]
    summoner1Casts: Mapped[int]
    summoner1Id: Mapped[int]
    summoner2Casts: Mapped[int]
    summoner2Id: Mapped[int]

class ParticipantEquipPerk(Base):
    __tablename__ = "equipperk"

    puuidTeamId = mapped_column(ForeignKey("participant.puuidTeamId"), primary_key = True)
    defensePerk: Mapped[int]
    flexPerk: Mapped[int]
    offensePerk: Mapped[int]
    primaryStylePerk = mapped_column(JSON)
    secondaryStylePerk = mapped_column(JSON)

class ParticipantShopTX(Base):
    __tablename__ = "shoptx"

    puuidTeamId = mapped_column(ForeignKey("participant.puuidTeamId"), primary_key = True)
    consumablesPurchased: Mapped[int]
    itemsPurchased: Mapped[int]
    goldEarned: Mapped[int]
    goldSpent: Mapped[int]

class Summoner(Base):
    __tablename__ = "summoner"

    puuid: Mapped[str] = mapped_column(primary_key = True)
    summonerId: Mapped[str] = mapped_column(unique = True)
    name: Mapped[str]
    level: Mapped[int]
    revisionDate: Mapped[datetime]

class League(Base):
    __tablename__ = "league"

    leagueId: Mapped[str] = mapped_column(primary_key = True)
    summonerId = mapped_column(ForeignKey("summoner.summonerId"))
    queueType: Mapped[str]
    tier: Mapped[str]
    rank: Mapped[str]
    wins: Mapped[int]
    losses: Mapped[int]
    leaguePoints: Mapped[int]
    veteran: Mapped[bool]
    inactive: Mapped[bool]
    freshBlood: Mapped[bool]
    hotStreak: Mapped[bool]

class Map(Base):
    __tablename__ = "map"
    
    mapId: Mapped[int] = mapped_column(primary_key = True)
    mapName: Mapped[str]

class GameMode(Base):
    __tablename__ = "gamemode"

    queueId: Mapped[int] = mapped_column(primary_key = True)
    mapName: Mapped[str | None]
    mapId: Mapped[int | None] = mapped_column(ForeignKey("map.mapId"))
    description: Mapped[str | None]

class Champion(Base):
    __tablename__ = "champion"
    default_scale = 4

    championId: Mapped[int] = mapped_column(primary_key = True)
    championName: Mapped[str]
    info = mapped_column(JSON, nullable = True)
    tags = mapped_column(ARRAY(String), nullable = True)
    hp = mapped_column(DECIMAL(scale=default_scale), nullable = True)
    hpperlevel = mapped_column(DECIMAL(scale=default_scale), nullable = True)
    mp = mapped_column(DECIMAL(scale=default_scale), nullable = True)
    mpperlevel = mapped_column(DECIMAL(scale=default_scale), nullable = True)
    movespeed = mapped_column(DECIMAL(scale=default_scale), nullable = True)
    armor = mapped_column(DECIMAL(scale=default_scale), nullable = True)
    armorperlevel = mapped_column(DECIMAL(scale=default_scale), nullable = True)
    spellblock = mapped_column(DECIMAL(scale=default_scale), nullable = True)
    spellblockperlevel = mapped_column(DECIMAL(scale=default_scale), nullable = True)
    attackrange = mapped_column(DECIMAL(scale=default_scale), nullable = True)
    hpregen = mapped_column(DECIMAL(scale=default_scale), nullable = True)
    hpregenperlevel = mapped_column(DECIMAL(scale=default_scale), nullable = True)
    mpregen = mapped_column(DECIMAL(scale=default_scale), nullable = True)
    mpregenperlevel = mapped_column(DECIMAL(scale=default_scale), nullable = True)
    crit = mapped_column(DECIMAL(scale=default_scale), nullable = True)
    critperlevel = mapped_column(DECIMAL(scale=default_scale), nullable = True)
    attackdamage = mapped_column(DECIMAL(scale=default_scale), nullable = True)
    attackdamageperlevel = mapped_column(DECIMAL(scale=default_scale), nullable = True)
    attackspeedperlevel = mapped_column(DECIMAL(scale=default_scale), nullable = True)
    attackspeed = mapped_column(DECIMAL(scale=default_scale), nullable = True)

class ShopItem(Base):
    __tablename__ = "shopitem"

    itemId: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str]
    basegold: Mapped[int]
    totalgold: Mapped[int]
    sellgold: Mapped[int]
    buildfrom = mapped_column(ARRAY(INTEGER), nullable = True)
    buildinto = mapped_column(ARRAY(INTEGER), nullable = True)
    tags = mapped_column(ARRAY(String), nullable = True)
    depth: Mapped[int | None]
    effect = mapped_column(JSON, nullable = True)
    stats = mapped_column(JSON, nullable = True)
    description: Mapped[str | None]

class Spell(Base):
    __tablename__ = "spell"

    championId = mapped_column(ForeignKey("champion.championId"))
    spellId: Mapped[int] = mapped_column(primary_key = True)
    spellName: Mapped[str]
    spellDesc: Mapped[str]