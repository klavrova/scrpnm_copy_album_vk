from time import sleep
import json
import html
from contextlib import suppress

import requests
from vklancer import api

from config import PHOTOS_LIMIT_BY_REQUEST

SLEEP_TIME = 0.34


def with_sleep(func):
    def decorated(*args, pause=SLEEP_TIME, **kwargs):
        sleep(pause)
        return func(*args, **kwargs)
    return decorated


class VKConnector(object):
    API_VERSION = '5.6'

    def __init__(self, token, version=API_VERSION):
        self.vk_api = api.API(token=token,
                              version=version)

    @with_sleep
    def get_pics(self, owner_id, album_id, offset=0, count=PHOTOS_LIMIT_BY_REQUEST):
        return self.vk_api.photos.get(owner_id=owner_id,
                                      album_id=album_id,
                                      offset=offset,
                                      count=count)['response']['items']

    @with_sleep
    def get_album_data(self, owner_id, album_id):
        result = self.vk_api.photos.getAlbums(owner_id=owner_id,
                                              album_ids=album_id)['response']['items'][0]
        title = result['title']
        size = result['size']
        return result, title, size

    @with_sleep
    def get_server(self, album_id, group_id):
        return self.vk_api.photos.getUploadServer(album_id=album_id,
                                                  group_id=group_id)['response']

    @with_sleep
    def create_album(self, title, group_id):
        return self.vk_api.photos.createAlbum(title=title,
                                              group_id=group_id,
                                              upload_by_admins_only=1)['response']

    @staticmethod
    def get_img_max_size(pic):
        keys = ['photo_2560', 'photo_1280', 'photo_807', 'photo_604']
        for key in keys:
            with suppress(KeyError):
                return pic[key]

    @staticmethod
    def save_img_local(link, name):
        r = requests.get(link)
        with open(name, 'wb') as f:
            f.write(r.content)

    @staticmethod
    def send_pic(upload_url, photo, pause=SLEEP_TIME):
        sleep(pause)
        img = {'file1': (photo, open(photo, 'rb'))}
        response = requests.post(upload_url, files=img)  # отправляем фотографию в вк
        return json.loads(response.text)

    @with_sleep
    def save_pic_vk(self, data, group_id, text):
        caption = html.unescape(text).replace('<br>', '\n')
        return self.vk_api.photos.save(server=data["server"],
                                       photos_list=data["photos_list"],
                                       album_id=data["aid"],
                                       hash=data["hash"],
                                       group_id=group_id,
                                       caption=caption)  # сохраняем фото
