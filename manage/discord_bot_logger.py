#!/usr/bin/python3.8

import os
import json
import datetime
import discord

LOG_DIRECTRY = 'data/log/'
DISCORD_SYSTEM_LOG_FILE_NAME = f'{LOG_DIRECTRY}/system_log.txt'
DISCORD_COMMAND_SUCCESS_LOG_FILE_NAME = f'{LOG_DIRECTRY}/command_success_log.txt'
DISCORD_COMMAND_FAILED_LOG_FILE_NAME = f'{LOG_DIRECTRY}/command_faild_log.txt'

MAX_LOG_FILE_SIZE = 1000000

# 存在しない,読み込めない場合は新規作成
def check_discord_log_data_file() -> bool:    
    if not os.path.exists(LOG_DIRECTRY):
        os.mkdir(LOG_DIRECTRY)
        return False
        
    return True

def backup_log(file_name:str):
    if not os.path.exists(file_name):
        return    
    if os.path.getsize(file_name) < MAX_LOG_FILE_SIZE:
        return
    
    has_extends = os.path.basename(file_name).find('.') != -1
    file_name = os.path.basename(file_name).split('.')[0]
    file_dir = os.path.dirname(file_name)    
    extends = '.' + os.path.basename(file_name).split('.')[1] if has_extends else ''

    for i in range(100000):
        backup_file_name = file_dir + '/' + file_name + i + extends
        if not os.path.exists(backup_file_name):            
            with open(file_name,'r') as file:
                log_data = file.read()
                
            with open(backup_file_name, 'w') as file:
                file.write(log_data)
            
            break

def write_log(file,  message: discord.Message, details=''):
    time = datetime.datetime.now()
    user_id = message.author.id
    channel_id = message.channel.id
    message_id = message.id
    message = message.content
    
    '| time | message-id | user-id | channel-id | message | details'
    log = f'{time} {message_id} <@!{user_id}> <#{channel_id}> {message} {details}' 
    print(log)
    with open(file, mode='a') as file:
        file.write(log)

def write_command_success_log(message: discord.Message):
    write_log(DISCORD_COMMAND_SUCCESS_LOG_FILE_NAME,message)
    
def write_command_failed_log(message: discord.Message):
    write_log(DISCORD_COMMAND_FAILED_LOG_FILE_NAME,message)
