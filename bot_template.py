#!/usr/bin/python3.8

import sys
import discord
from discord.ext import commands, tasks
from .manage import *

GOOD_EMOTICON = '☑'
BAD_EMOTICON = '❌'
COMMAND_PREFIX = '!'

COMMAND_INSPECT = 'inspect'
COMMAND_QUIT = 'quit'

class CommandArgs:
    def __init__(self,message: discord.Message, command_args:list) -> None:
            self.message = message
            self.command_args = command_args

class BotTemplate(discord.Client):
    def __init__(self,bot_name , intents: discord.Intents, command_prefix=COMMAND_PREFIX, **options) -> None:
        super().__init__(intents=intents, **options)
        
        
        check_discord_log_data_file()
        
        self.bot_name = bot_name
        self.post_channel_id = DiscordData.get_post_channel_id()
        self.command_channel_id = DiscordData.get_command_channel_id()
        self.command_log_channel_id = DiscordData.get_command_log_channel_id()
        self.command = {}
        self.prefix = command_prefix

        self.add_command(f'{COMMAND_INSPECT} {self.bot_name}', self.inspect)

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
        
        if await func[0](CommandArgs(message, func[1])):
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
        
    async def inspect(self, command: CommandArgs) -> bool: 
        command_list = get_command(self.command)

        inspect_view = '## command list\n'
        inspect_view += '---\n'
        for i in command_list:
            inspect_view += f'`{i}`\n'
        
        channel_view = [
            '\n## channel\n',
            f'post: <#{DiscordData.get_post_channel_id()}>',
            f'command: <#{DiscordData.get_command_channel_id()}>',
            f'command log: <#{DiscordData.get_command_log_channel_id()}>',
            'reaction channel list',
            '---',
        ]
        inspect_view += '\n'.join(channel_view)
        reaction_view = DiscordData.get_reaction_channel_id()
        for i in reaction_view:
            inspect_view += f'<#{i}> \n'
        
        await command.message.add_reaction(GOOD_EMOTICON)
        await self.post(command.message.channel.id, inspect_view)
        return True
    

def main(command_prefix = COMMAND_PREFIX):
    if not DiscordData.check_discord_data_file():
        return

    intents = discord.Intents.default()
    intents.message_content = True
    client = BotTemplate(
        bot_name='hoge',
        intents=intents,
        command_prefix=command_prefix
        )
    client.run(DiscordData().get_token())

if __name__ == '__main__':
    main()
