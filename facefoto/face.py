import base64
import json
import os
import traceback
from threading import Thread

import requests as r
from flask import (
    Blueprint, request, jsonify, current_app
)
from flask_uploads import UploadSet, IMAGES, configure_uploads

from facefoto.dao import *
from facefoto.oss_util import upload_file
from facefoto.tasks import find_similar_task

bp = Blueprint('face', __name__)

task_id = 0
head_group_id = None


# 上传图片
@bp.route('/modify', methods=['POST'])
def upload():
    """upload a photo to group."""
    global local_filename
    global task_id
    head_group_id = current_app.config['HEAD_GROUP_ID']
    if request.method == 'POST':
        user_id = request.form['user_id']
        followed_group_id = request.form['group_id']
        if not followed_group_id:
            return jsonify({'code': 400, 'msg': 'group_id is required.'})
        elif not user_id:
            return jsonify({'code': 400, 'msg': 'user_id is required.'})

        if 'photo' not in request.files:
            return jsonify({'code': 400, 'msg': 'photo is required.'})
        head_pic = request.files['photo']

        try:
            # 1、校验组是否存在
            group = get_group(head_group_id)
            if not group:
                return jsonify({'code': 400, 'msg': 'can not found group by id [{0}]'.format(head_group_id)})
            photos = UploadSet('photos', IMAGES)
            configure_uploads(current_app, photos)
            filename = photos.save(head_pic)
            local_filename = photos.path(filename)
            oss_dir = group[1]
            oss_filename = '{0}{1}'.format(group[1], filename)
            if not oss_dir.endswith("/"):
                oss_filename = '{0}/{1}'.format(group[1], filename)

            # 2、获得图片的base64编码
            photo_base64 = base64.b64encode(open(local_filename, 'rb').read())
            encode_str = str(photo_base64, 'utf-8')

            # 3、通过第三方接口获得图片的特征值
            ret = r.post(current_app.config['GET_FEATURE_URL'], data=json.dumps({'image': encode_str}),
                         headers={'content-type': 'application/json'})
            response = json.loads(ret.text)

            if 'body' in response:
                body = response['body']
                # 4、上传图片到oss
                oss_url = upload_file(oss_filename, local_filename)
                # 5、保存photo数据到db
                head_pic = get_image_by_muiti_condition(filename, oss_filename, int(head_group_id))
                global head_pic_id
                if not head_pic:
                    head_pic_id = add_image(filename, oss_filename, int(head_group_id), json.dumps(body))
                else:
                    head_pic_id = head_pic[0]
                    update_image(filename, oss_filename, int(head_group_id), json.dumps(body), head_pic_id)
                # 6、保存用户、头像图片和关注组的关系
                face = get_face_by_user_id_and_grou_id(user_id, followed_group_id)
                if not face:
                    add_face(user_id, followed_group_id, head_pic_id)
                else:
                    update_face(user_id, followed_group_id, head_pic_id, face[0])
                # 7、添加一个相似图片查找任务，使用用户头像去所关注的组中找相似的图片，结果缓存到结果表
                task_id += 1
                Thread(target=find_similar_task,
                       args=(current_app._get_current_object(), "face_%s" % task_id, followed_group_id, head_pic_id,)
                       ).start()

                # 8、返回头像保存结果
                return jsonify(
                    {'code': 200, 'image_id': head_pic_id, 'url': oss_url,
                     'url_express': current_app.config['OSS_URL_EXPIRES'],
                     'msg': 'modify head image success.'})
            else:
                return jsonify(response)
        except Exception as e:
            traceback.print_exc()
            return jsonify({'code': 500, 'error': '{0}'.format(e)})
        finally:
            # 6、删除临时图片
            try:
                if os.path.isfile(local_filename):
                    os.remove(local_filename)
            except FileNotFoundError:
                print("delete not exits file")
            except Exception:
                traceback.print_exc()
    else:
        return jsonify({'code': 400, 'msg': 'upload image failed.'})
