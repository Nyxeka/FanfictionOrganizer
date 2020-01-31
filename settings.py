import configparser

config = configparser.ConfigParser()

config['DEFAULT'] = {'LibraryPath' : './'}

def save_config():
    with open('config.ini', 'w') as config_file:
        config.write(config_file)

def load_config():
    with open('config.ini', 'r') as config_file:
        config.read(config_file)