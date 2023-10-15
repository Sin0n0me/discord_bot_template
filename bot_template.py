import sys
import discord
from discord.ext import commands, tasks
from manage import *

GOOD_EMOTICON = '☑'
BAD_EMOTICON = '❌'
COMMAND_PREFIX = '!'

COMMAND_INSPECT = 'inspect'
COMMAND_QUIT = 'quit'

def create_command_dict(command:list, func) -> dict:
    if command == []:
        return {}
    if len(command) > 1:
        return {command[0] : create_command_dict(command[1:], func)}
    return {command[0]: func}

# 0: func
# 1: args
def get_command_func(command:list, comamnd_dict:dict) -> tuple:
    if command == []:
        return ()
    current_word = command[0]
    if current_word not in comamnd_dict:
        return ()    
    if len(command) == 1:
        func = comamnd_dict[current_word]
        # コマンド実行まで足らない場合
        if type(func) == dict:
            return ()
        
        return (func, None)        
    if current_word not in comamnd_dict:
        return ()

    # 次もキーが存在した場合は再帰
    next_dict = comamnd_dict[current_word]
    if command[1] in next_dict:
        return get_command_func(comamnd_dict=comamnd_dict[current_word],command=command[1:])
    
    return (comamnd_dict[current_word], command[1:])

def get_command(comamnd_dict:dict, pre_command:str = '') -> list:
    command_list = []
    for key in comamnd_dict.keys():
        temp = comamnd_dict[key]
        if type(temp) == dict:
            command_list.extend(get_command(comamnd_dict=temp,pre_command=f'{key} '))
        else:
            command_list.append(f'{pre_command}{key}')
        
    return command_list

class BotTemplate(discord.Client):
    def __init__(self,bot_name , intents: discord.Intents, command_prefix, **options) -> None:
        super().__init__(intents=intents, **options)
        
        check_discord_log_data_file()
        
        self.bot_name = bot_name
        self.post_channel_id = get_post_channel_id()
        self.command_channel_id = get_command_channel_id()
        self.command_log_channel_id = get_command_log_channel_id()
        self.command = {}
        self.prefix = command_prefix

        self.add_command(f'{COMMAND_INSPECT} {self.bot_name}', self.inspect)
        
        print(get_command(self.command))

    def add_command(self, command:str, func):
        command_dict = create_command_dict(command.split(' '), func)
        if command_dict == {}:
            return
        
        self.command.update(command_dict)
                
    async def exec_command(self, command:str, message: discord.Message):        
        func = get_command_func(command.split(' '), self.command)
        if func == ():
            write_command_failed_log(message)
            await message.add_reaction(BAD_EMOTICON)
            await self.replay(message.channel.id, message.author.id, 'unknown command')
            return
        
        print(func)
        if await func[0](message, func[1]):
            write_command_success_log(message)
            await message.add_reaction(GOOD_EMOTICON)
        else:
            write_command_failed_log(message)
            await message.add_reaction(BAD_EMOTICON)
    
    #
    async def on_ready(self):
        await self.change_presence(activity=discord.Game("Python"))
        await self.post(
            channel_id=self.command_log_channel_id,
            message="Start bot"
        )

    # サーバにメッセージが送信されたとき
    async def on_message(self, message: discord.Message):
        # プレフィックスが!以外ならば何もしない
        if not message.content.startswith(COMMAND_PREFIX):
            return
        
        # bot自身の場合何もしない(自身のリプライに無限に反応し続けるので)
        if message.author == self.user:
            return
        
        if message.content[1:] == f'{COMMAND_QUIT} {self.bot_name}':
            await self.quit(message)
            return
        
        # コマンド実行
        await self.exec_command(message.content[1:], message)

    #
    async def on_socket_response(self, message):
        pass

    # メッセージ送信
    async def post(self, channel_id: int, message: str,  attachment=None):
        await self.get_channel(channel_id).send(message, file=attachment)

    # 返信
    async def replay(self, channel_id, to: int, message: str, attachment=None):
        await self.post(channel_id, f"<@!{to}> \n{message}", attachment=attachment)

    # 終了
    async def quit(self, message: discord.Message): 
        await message.add_reaction(GOOD_EMOTICON)
        await self.post(message.channel.id, 'Bye')
        await self.close()
        sys.exit(0)
        
    async def inspect(self, message: discord.Message, args:list) -> bool: 
        command_list = get_command(self.command)

        comamnd_view = 'command list\n'
        comamnd_view += '---\n'
        for i in command_list:
            comamnd_view += f'`{i}`\n'
        
        await message.add_reaction(GOOD_EMOTICON)
        await self.post(message.channel.id, comamnd_view)
        return True
    

def main(command_prefix = COMMAND_PREFIX):
    if not check_discord_data_file():
        return

    intents = discord.Intents.default()
    intents.message_content = True
    client = BotTemplate(
        bot_name='hoge',
        intents=intents,
        command_prefix=command_prefix
        )
    client.run(get_token())

if __name__ == '__main__':
    main()
