import os
import json

DISCORD_DATA_FILE_NAME = 'data/discord_data.json'
KEY_TOKEN = 'Token'
KEY_ADMINISTRATOR_ID = 'Administrator ID'
KEY_OPERATOR_ID = 'Operator ID'
KEY_REACTION_CHANNEL_ID = 'Reaction channel ID'
KEY_POST_CHANNEL_ID = 'Post channel ID'
KEY_COMMAND_CHANNEL_ID = 'Command channel ID'
KEY_COMMAND_LOG_CHANNEL_ID = 'Command log ID'

JSON_DATA_FORMAT = {
    KEY_TOKEN: '',
    KEY_ADMINISTRATOR_ID: 0,
    KEY_OPERATOR_ID: [],
    KEY_REACTION_CHANNEL_ID:[],
    KEY_POST_CHANNEL_ID: 0,
    KEY_COMMAND_CHANNEL_ID: 0,
    KEY_COMMAND_LOG_CHANNEL_ID: 0,
}
        
def create_discord_data_file():
    directry = os.path.dirname(DISCORD_DATA_FILE_NAME)    
    if not os.path.exists(directry):
        os.mkdir(directry)

    with open(DISCORD_DATA_FILE_NAME, 'w') as file:
        json.dump(fp=file, obj=JSON_DATA_FORMAT, indent=4)

def get_bot_data(key):
    if not os.path.exists(DISCORD_DATA_FILE_NAME):
        print('not found data file')
        return None

    with open(DISCORD_DATA_FILE_NAME, 'r') as file:
        discord_data: dict = json.load(file)
        
    if key not in discord_data:
        print(f'not found key: {key}')
        return None
    
    return discord_data[key]

def update_bot_data(key, value, is_overwrite=False):
    with open(DISCORD_DATA_FILE_NAME, 'r') as file:
        discord_data: dict = json.load(file)

    if type(value) is list and not is_overwrite:
        discord_data[key].append(value)
        discord_data[key] = list(set(discord_data[key]))
    else:        
        discord_data[key] = value       

    with open(DISCORD_DATA_FILE_NAME, 'w') as file:
        json.dump(fp=file, obj=discord_data, indent=4)

def delete_bot_data(key, value=None):
    with open(DISCORD_DATA_FILE_NAME, 'r') as file:
        discord_data: dict = json.load(file)
    
    delete_data = None
    if type(value) is list:
        delete_data = [data for data in discord_data[key] if data == value]

    discord_data[key] = delete_data

    with open(DISCORD_DATA_FILE_NAME, 'w') as file:
        json.dump(fp=file, obj=discord_data, indent=4)

### 

class DiscordData():
    couner = 0
    
    @staticmethod
    def get_token():
        if DiscordData.couner != 0:
            return None
        DiscordData.couner += 1
        return get_bot_data(KEY_TOKEN)

    @staticmethod
    def get_post_channel_id() -> int:
        return get_bot_data(KEY_POST_CHANNEL_ID)

    @staticmethod
    def get_command_channel_id() -> int:
        return get_bot_data(KEY_COMMAND_CHANNEL_ID)

    @staticmethod
    def get_command_log_channel_id() -> int:
        return get_bot_data(KEY_COMMAND_LOG_CHANNEL_ID)

    @staticmethod
    def add_bot_operator_id(command_issuer_id, member_id) -> bool:
        if not DiscordData.is_admin(command_issuer_id) and not DiscordData.is_bot_operator(command_issuer_id):
            return False
        
        update_bot_data(KEY_OPERATOR_ID, member_id)
        return True

    @staticmethod
    def remove_bot_operator_id(command_issuer_id, member_id) -> bool:
        if not DiscordData.is_admin(command_issuer_id) and not DiscordData.is_bot_operator(command_issuer_id):
            return False
        
        delete_bot_data(KEY_OPERATOR_ID, member_id)
        return True

    @staticmethod
    def is_bot_operator(command_issuer_id) -> bool:
        id_liet = get_bot_data(KEY_OPERATOR_ID)
        if id_liet is None:
            return False
        if id_liet == []:
            return False
        return command_issuer_id in set(id_liet) 
        
    @staticmethod
    def add_reaction_channel_id(command_issuer_id, channel_id) -> bool:
        if not DiscordData.is_admin(command_issuer_id) and not DiscordData.is_bot_operator(command_issuer_id):
            return False
        
        update_bot_data(KEY_REACTION_CHANNEL_ID, channel_id)
        return True

    @staticmethod
    def remove_reaction_channel_id(command_issuer_id, channel_id) -> bool:
        if not DiscordData.is_admin(command_issuer_id) and not DiscordData.is_bot_operator(command_issuer_id):
            return False
        
        delete_bot_data(KEY_REACTION_CHANNEL_ID, channel_id)
        return True

    @staticmethod
    def get_reaction_channel_id() -> list:
        return list(get_bot_data(KEY_REACTION_CHANNEL_ID))

    @staticmethod
    def is_reaction_channel(channel_id) -> bool:
        id_liet = get_bot_data(KEY_REACTION_CHANNEL_ID)
        if id_liet is None:
            return False
        if id_liet == []:
            return False
        
        return channel_id in set(id_liet) 

    @staticmethod
    def is_admin(command_issuer_id) -> bool:
        id = get_bot_data(KEY_ADMINISTRATOR_ID)
        if not id:
            return False
        
        return id == command_issuer_id
    
    # 存在しない,読み込めない場合は新規作成
    @staticmethod
    def check_discord_data_file() -> bool:
        if not os.path.exists(DISCORD_DATA_FILE_NAME):
            create_discord_data_file()
            return False
            
        try:
            with open(DISCORD_DATA_FILE_NAME, 'r') as file:
                json.load(file)        
        except:
            create_discord_data_file()
            return False
            
        return True
