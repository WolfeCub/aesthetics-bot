#!/usr/bin/env python3
import os
import json

def get_unlinked_files(source, target):
    for file in os.listdir(source):
        if os.path.isfile(os.path.join(source, file)) and \
           not os.path.exists(os.path.join(target, file)):
            yield file

def read_new_config(sample_path):
    config = {}
    with open(sample_path, 'r') as f:
        sample_config = json.loads(f.read())
        for key in sample_config:
            value = input(f'{key}: ')
            if value is not None and value != '':
                config[key] = value

    return config

def write_config_to_file(config, path):
    with open(path, 'w') as outfile:
        json.dump(config, outfile, indent=2)

if __name__ == '__main__':
    # Move to this files location
    dname = os.path.dirname(os.path.abspath(__file__))
    os.chdir(dname)

    # Create config on first run
    if not os.path.exists('config.json'):
        print("No config file found. Creating 'config.json' ...")
        print('Enter the value for each config setting. Pressing enter will skip it.')
        conf = read_new_config('docs/config.json.sample')
        write_config_to_file(conf, 'config.json')
    else:
        print('Config file already exists. Skipping ...')

    # Enable desired modules
    for file in get_unlinked_files('mods-available/', 'mods-enabled/'):
        inpt = input(f'Link {file}? (y/N): ')
        if inpt != 'y':
            print(f'Skipping {file}')
        elif os.path.exists(f'mods-enabled/{file}'):
            print(f'{file} is already enabled')
        else:
            os.symlink(f'{dname}/mods-available/{file}', f'{dname}/mods-enabled/{file}')
