#!/usr/bin/python3.8

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

def merge_nested_dicts(d1:dict, d2:dict):
    for key, value in d2.items():
        if key in d1:
            if isinstance(d1[key], dict) and isinstance(value, dict):
                merge_nested_dicts(d1[key], value)
            else:
                d1[key] = value
        else:
            d1[key] = value
    return d1