import datetime
import json
import time
from threading import Thread

import requests as r
from flask import (
    current_app)

from facefoto.dao import *
from facefoto.distance_util import find_similar
from facefoto.oss_util import get_oss_url

now = lambda: int(round(time.time() * 1000))
nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def find_similar_task(app, _task_id, group_id, photo_id):
    with app.app_context():
        start = now()
        print("Begin task[%s] for group_id:%s, photo_id:%s" % (_task_id, group_id, photo_id))
        head_group_id = current_app.config['HEAD_GROUP_ID']
        # 1、获得photo
        image = get_image(photo_id)
        if not image:
            return print('cant not find image by id {0}'.format(photo_id))
        photo_group_id = image[3]
        caches = []
        if photo_group_id == head_group_id:
            print("head image modify, find similar photos from group[%s]" % group_id)
            # 2、获得指定group_id下的所有photo
            target_images = get_images_by_group_id(group_id)
            if not target_images:
                return print('cant not find any image by group id {0}'.format(group_id))
            # 3、比对features值
            sorted_matched_images = find_similar(image, target_images)
            if sorted_matched_images:
                face = get_face_by_photo_id(photo_id)
                user_id = face[0]
                for matched in sorted_matched_images:
                    caches.append(add_or_update_cache(user_id, group_id, matched[0]))
        else:
            print("upload a photo, find similar head image from group[%s]" % head_group_id)
            # 2、获得所有关注该group的用户头像
            faces = get_faces_by_group_id(group_id)
            target_images = []
            for one in faces:
                target_images.append(get_image(one[3]))
            # 3、比对features值
            sorted_matched_images = find_similar(image, target_images)
            if sorted_matched_images:
                for matched in sorted_matched_images:
                    face = get_face_by_photo_id(matched[0])
                    user_id = face[0]
                    caches.append(add_or_update_cache(user_id, group_id, image[0]))
        Thread(target=notify_task,
               args=(current_app._get_current_object(), caches,)
               ).start()
        # time.sleep(10)
        print(caches)
        print("Finish task[%s] for group_id:%s, photo_id:%s ,take %d milliseconds" % (
            _task_id, group_id, photo_id, now() - start))


def notify_task(app, cache_ids):
    with app.app_context():
        notify_url = current_app.config['NOTIFY_URL']
        expires = current_app.config['OSS_URL_EXPIRES']
        print("begin to send notify task")
        data = []
        notified = []
        for cache_id in cache_ids:
            if cache_id:
                cache = get_cache(cache_id)
                notified.append(cache)
                photo = get_image(cache[3])
                oss_url = get_oss_url(photo[2], expires)
                one = {'user_id': cache[1], 'group_id': cache[2], 'image_id': cache[3], 'url': oss_url,
                       'url_express': expires}
                # start = now()
                data.append(one)
        result = {'notify_time': nowTime, 'data': data}
        try:
            r.post(notify_url, data=json.dumps(result), timeout=5.0,
                   headers={'content-type': 'application/json'})
        except Exception as e:
            print(e)
            # traceback.print_exc()
        for temp in notified:
            update_cache(temp[1], temp[2], temp[3], True, temp[0])
        print("send notify to %s finish" % notify_url)
