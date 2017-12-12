import configparser
import os
import sys

filename = 'config.ini'
file = os.path.join(os.path.dirname(sys.argv[0]), filename)
config = configparser.RawConfigParser()
config.read(file)
TEST_GROUP = int(config.get('Groups', 'Test'))
PRODUCTION_GROUP = int(config.get('Groups', 'Production'))
TOKENS = [i[1] for i in config.items('Tokens')]

PHOTOS_LIMIT_BY_REQUEST = 1000
PHOTOS_LIMIT_BY_TIME = 2000  # максимальное к-во фотографий, которые вк даёт загружать пользователю за 6 часов
