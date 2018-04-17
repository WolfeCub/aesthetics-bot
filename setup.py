import os
import json
from json.decoder import JSONDecodeError
from contextlib import suppress

def files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file

def read_new_config(sample_path):
    config = {}
    with open(sample_path, 'r') as f:
        sample_config = json.loads(f.read())
        for key in sample_config:
            value = input(f'{key}: ')
            with suppress(JSONDecodeError):
                value = json.loads(value)
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
        print('Enter the value for each config setting. Pressing enter will skip it.')
        conf = read_new_config('docs/config.json.sample')
        write_config_to_file(conf, 'config.json')

    print('\nSelect the modules you wish to enable: ')
    # Enable desired modules
    for file in files('mods-available/'):
        inpt = input(f'Link {file}? (y/N): ')
        if inpt != 'y':
            print(f'Skipping {file}')
        elif os.path.exists(f'mods-enabled/{file}'):
            print(f'{file} is already enabled')
        else:
            os.symlink(f'{dname}/mods-available/{file}', f'{dname}/mods-enabled/{file}')
