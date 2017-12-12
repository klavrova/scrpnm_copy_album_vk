import argparse

from vk_connector import VKConnector
from config import TOKENS, PRODUCTION_GROUP, TEST_GROUP, PHOTOS_LIMIT_BY_REQUEST, PHOTOS_LIMIT_BY_TIME

IMG_KEY = 'link'
TEXT_KEY = 'text'
SAVED_PHOTO_NAME = 'img.jpg'


def parse_album_link(production, test):
    parser = argparse.ArgumentParser(description='Программа для перезаливки альбомов vk в свою группу')
    parser.add_argument('link', metavar='L', type=str, help='ссылка на фотоальбом vk')
    parser.add_argument('-p', action='store_true', help='заливать в основную группу')
    args = parser.parse_args()
    group = production if args.p else test
    album_link = args.link
    return album_link, group


def copy_album(album_link, group):
    page_id, album_id = album_link[20:].split('_')
    api = VKConnector(token=TOKENS[0])
    album_data, album_name, album_size = api.get_album_data(page_id, album_id)  # get album data
    counter = 0
    vk_pictures = []
    while counter < album_size:
        vk_pictures.extend(api.get_pics(page_id, album_id, offset=counter))
        counter += PHOTOS_LIMIT_BY_REQUEST
    pictures = [{IMG_KEY: api.get_img_max_size(p), TEXT_KEY: p[TEXT_KEY]} for p in vk_pictures]
    new_album = api.create_album(album_name, group)  # create album and get id
    tokens = iter(TOKENS)
    images = iter(pictures)
    image = next(images)
    count = 1
    for i in range((album_size // PHOTOS_LIMIT_BY_REQUEST + 1) // 2 + 1):
        token = next(tokens)
        api = VKConnector(token)
        server = api.get_server(new_album['id'], group)  # get server
        for j in range(PHOTOS_LIMIT_BY_TIME):
            api.save_img_local(image[IMG_KEY], SAVED_PHOTO_NAME)  # save photo
            upl_result = api.send_pic(server['upload_url'], SAVED_PHOTO_NAME)
            api.save_pic_vk(upl_result, group, image[TEXT_KEY])
            print(f'data saved: {count}/{album_size}')
            if count == album_size:
                exit(0)
            else:
                count += 1
                try:
                    image = next(images)
                except StopIteration:
                    break


if __name__ == '__main__':
    copy_album(*parse_album_link(PRODUCTION_GROUP, TEST_GROUP))

