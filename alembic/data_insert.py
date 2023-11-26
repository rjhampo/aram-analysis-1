import json, sqlalchemy as core, sqlalchemy.orm as orm, os, dotenv
from sqlalchemy.dialects.postgresql import insert
import current_model

dotenv.load_dotenv()
source_dir = os.environ.get("CONSTANT_SOURCE_DIR")
engine = core.create_engine(os.environ.get("SERVER_URL2"), echo=True)

session_fact = orm.sessionmaker(engine)

def insert_map_data():
    with open(os.path.join(source_dir, "map.json")) as inp_file:
        inp_json = json.loads(inp_file.read())
        insert_array = [{'mapId': int(row['MapId']), 'mapName': row['MapName']} for row in inp_json['data'].values()]
        with session_fact.begin() as session:
            session.execute(insert(current_model.Map).on_conflict_do_nothing(), insert_array)

def insert_queue_data():
    with open(os.path.join(source_dir, "queues.json")) as inp_file:
        inp_json = json.loads(inp_file.read())
        insert_array = [{'queueId': row['queueId'], 'mapName': row['map'], 'description': row['description']} for row in inp_json]
        with session_fact.begin() as session:
            for i, value in enumerate(insert_array):
                stmt = core.select(current_model.Map).where(current_model.Map.mapName==value['mapName'])
                result = session.execute(stmt).all()
                if not result: insert_array[i]['mapId'] = None
                else: insert_array[i]['mapId'] = result[0][0].mapId
            session.execute(insert(current_model.GameMode).on_conflict_do_nothing(), insert_array)

def insert_champ_data():
    with open(os.path.join(source_dir, "champion.json"), encoding='utf8') as inp_file:
        inp_json = json.loads(inp_file.read())
        insert_array = []
        for row in inp_json['data'].values():
            buf = {'championId': row['key'], 'championName': row['name'], 'info': row['info'], 'tags': row['tags']}
            for stat_key, stat_value in row['stats'].items():
                buf[stat_key] = stat_value
            insert_array.append(buf)
        
        insert_array.append({'championId': 999, 'championName': 'Any'}) # Dummy champion
        with session_fact.begin() as session:
            session.execute(insert(current_model.Champion).on_conflict_do_nothing(), insert_array)

def insert_item_data():
    with open(os.path.join(source_dir, "item.json")) as inp_file:
        inp_json = json.loads(inp_file.read())
        insert_array = [{'itemId': key, 'name': item.get('name'), 'basegold': item['gold']['base'],
                         'totalgold': item['gold']['total'], 'sellgold': item['gold']['sell'],
                         'buildfrom': item.get('from'), 'buildinto': item.get('into'), 'tags': item.get('tags'),
                         'depth': item.get('depth'), 'effect': item.get('effect'), 'stats': item.get('stats'),
                         'description': item.get('description')} for key, item in inp_json['data'].items()]
        insert_array.append({'itemId': 0, 'name': 'None', 'basegold':0, 'totalgold': 0, 'sellgold': 0}) # Dummy item
        with session_fact.begin() as session:
            session.execute(insert(current_model.ShopItem).on_conflict_do_nothing(), insert_array)

def insert_spell_data():
    with open(os.path.join(source_dir, "championFull.json"), encoding='utf8') as inp_file:
        inp_json = json.loads(inp_file.read())
        insert_array = [{'championId': champion['key'],
                         'spellId': int(str(champion['key']) + str(i)),
                         'spellName': spell['name'],
                         'spellDesc': spell['tooltip']} for champion in inp_json['data'].values() for i, spell in enumerate(champion['spells'])]
    with open(os.path.join(source_dir, "summoner.json"), encoding='utf8') as inp_file:
        inp_json = json.loads(inp_file.read())
        for i, value in enumerate(inp_json['data'].values()):
            insert_array.append({'championId': 999, 'spellId': int('999' + str(i)), 'spellName': value['name'], 'spellDesc': value['tooltip']})
    with session_fact.begin() as session:
        session.execute(insert(current_model.Spell).on_conflict_do_nothing(), insert_array)

def add_fundamental_data():
    insert_map_data()
    insert_queue_data()
    insert_item_data()
    insert_champ_data()
    insert_spell_data()

def remove_fundamental_data():
    with session_fact.begin() as session:
        session.execute(core.delete(current_model.Spell))
        session.execute(core.delete(current_model.Champion))
        session.execute(core.delete(current_model.ShopItem))
        session.execute(core.delete(current_model.GameMode))
        session.execute(core.delete(current_model.Map))