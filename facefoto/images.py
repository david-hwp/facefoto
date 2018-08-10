import base64
import json
import os
import time
import traceback
from threading import Thread

import requests as r
from flask import (
    Blueprint, request, jsonify, current_app
)
from flask_uploads import UploadSet, IMAGES, configure_uploads

from facefoto.dao import *
from facefoto.distance_util import find_similar
from facefoto.face import find_similar_task
from facefoto.groups import get_group
from facefoto.oss_util import upload_file, get_oss_url, remove_file

bp = Blueprint('images', __name__)
task_id = 0


# 上传图片
@bp.route('', methods=['POST'])
def images():
    """upload a photo to group."""
    global local_filename
    global task_id
    if request.method == 'POST':
        group_id = request.form['group_id']
        if not group_id:
            return jsonify({'code': 400, 'msg': 'group_id is required.'})
        if 'photo' not in request.files:
            return jsonify({'code': 400, 'msg': 'photo is required.'})
        photo = request.files['photo']
        try:
            # 1、校验组是否存在
            group = get_group(group_id)
            if not group:
                return jsonify({'code': 400, 'msg': 'can not found group by id [{0}]'.format(group_id)})
            photos = UploadSet('photos', IMAGES)
            configure_uploads(current_app, photos)
            filename = photos.save(photo)
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
                image_id = add_image(filename, oss_filename, int(group_id), json.dumps(body))
                task_id += 1
                Thread(target=find_similar_task,
                       args=(current_app._get_current_object(), "image_%s" % task_id, group_id, image_id,)
                       ).start()
                return jsonify(
                    {'code': 200, 'image_id': image_id, 'url': oss_url,
                     'url_express': current_app.config['OSS_URL_EXPIRES'],
                     'msg': 'upload image success.'})
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


# 从oss中上传图片
@bp.route('/oss', methods=['POST'])
def images_from_oss():
    """upload a photo to group."""
    global local_filename
    if request.method == 'POST':
        data = request.get_json()
        group_id = data['group_id']
        oss_url = data['oss_url']
        oss_filename = data['oss_filename']

        try:
            # 1、校验组是否存在
            group = get_group(group_id)
            if not group:
                return jsonify({'code': 400, 'msg': 'can not found group by id [{0}]'.format(group_id)})
            filename = oss_filename.split('/')[-1]
            local_filename = current_app.instance_path + "/" + filename
            res = r.get(url=oss_url)
            if res:
                with open(local_filename, 'wb') as f:
                    f.write(res.content)
            else:
                time.sleep(0.1)
                res1 = r.get(url=oss_url)
                with open(local_filename, 'wb') as f:
                    f.write(res1.content)
            # 2、获得图片的base64编码
            photo_base64 = base64.b64encode(open(local_filename, 'rb').read())
            encode_str = str(photo_base64, 'utf-8')

            # 3、通过第三方接口获得图片的特征值
            ret = r.post(current_app.config['GET_FEATURE_URL'], data=json.dumps({'image': encode_str}),
                         headers={'content-type': 'application/json'})
            response = json.loads(ret.text)

            if 'body' in response:
                body = response['body']
                # 5、保存photo数据到db
                image_id = add_image(filename, oss_filename.split(current_app.config['BUCKET_NAME'])[-1], group_id,
                                     json.dumps(body))

                return jsonify(
                    {'code': 200, 'image_id': image_id, 'url': oss_url,
                     'url_express': current_app.config['OSS_URL_EXPIRES'],
                     'msg': 'upload image success.'})
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


# 上传图片
@bp.route('/searchByPhoto', methods=['POST'])
def search_by_photo():
    """upload a photo to group."""
    global local_filename
    if request.method == 'POST':
        group_id = request.form['group_id']
        if not group_id:
            return jsonify({'code': 400, 'msg': 'group_id is required.'})
        if 'photo' not in request.files:
            return jsonify({'code': 400, 'msg': 'photo is required.'})
        photo = request.files['photo']
        try:
            # 1、校验组是否存在
            group = get_group(group_id)
            if not group:
                return jsonify({'code': 400, 'msg': 'can not found group by id [{0}]'.format(group_id)})
            # 2、获得指定group_id下的所有photo
            target_images = get_images_by_group_id(group_id)
            if not target_images:
                return jsonify({'code': 400, 'msg': 'cant not find any image by group id {0}'.format(group_id)})
            limit = float(current_app.config['FEATURES_MAX_MATCH_LIMIT'])
            limit = 2 * (1 - limit)
            print("limit {0}".format(limit))
            # 3、上传图片
            photos = UploadSet('photos', IMAGES)
            configure_uploads(current_app, photos)
            filename = photos.save(photo)
            local_filename = photos.path(filename)

            # 4、获得图片的base64编码
            photo_base64 = base64.b64encode(open(local_filename, 'rb').read())
            encode_str = str(photo_base64, 'utf-8')

            # 5、通过第三方接口获得图片的特征值
            ret = r.post(current_app.config['GET_FEATURE_URL'], data=json.dumps({'image': encode_str}),
                         headers={'content-type': 'application/json'})
            response = json.loads(ret.text)
            print(filename)

            if 'body' in response:
                body = response['body']
                image = (None, filename, None, int(group_id), json.dumps(body))
                # 6、比对feature值
                sorted_matched_images = find_similar(image, target_images)
                result_body = []
                for matched in sorted_matched_images:
                    oss_path = matched[2]
                    expires = current_app.config['OSS_URL_EXPIRES']
                    oss_url = get_oss_url(oss_path, expires)
                    result_body.append({'id': matched[0], 'name': matched[1], 'url': oss_url, 'expires': expires})

                return jsonify({'code': 200, 'data': result_body})
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


# 根据oss路径搜索相似图片
@bp.route('/searchByOssPath', methods=['POST'])
def search_by_oss_path():
    if request.method == 'POST':
        data = request.get_json()
        try:
            group_id = data['group_id']
            oss_path = data['oss_path']
            print(oss_path)

            # 1、获得photo
            image = get_image_by_oss_path(oss_path)
            # 2、获得指定group_id下的所有photo
            target_images = get_images_by_group_id(group_id)
            if not image:
                return jsonify({'code': 400, 'msg': 'cant not find image by oss_path{0}'.format(oss_path)})
            if not target_images:
                return jsonify({'code': 400, 'msg': 'cant not find any image by group id {0}'.format(group_id)})

            # 3、比对features值
            sorted_matched_images = find_similar(image, target_images)
            result_body = []
            for matched in sorted_matched_images:
                result_body.append({'id': matched[0], 'name': matched[1]})
            return jsonify({'code': 200, 'data': result_body})
        except Exception as e:
            return jsonify({'code': 500, 'error': "{0}".format(e)})


# 根据图片id和分组id搜索图片
@bp.route('/search', methods=['GET'])
def search():
    try:
        group_id = request.args.get('group_id')
        image_id = request.args.get('image_id')
        if not image_id:
            return jsonify({'code': 400, 'msg': 'image_id is required.'})
        elif not group_id:
            return jsonify({'code': 400, 'msg': 'group_id is required.'})
        # 1、获得photo
        image = get_image(image_id)
        # 2、获得指定group_id下的所有photo
        target_images = get_images_by_group_id(group_id)
        if not image:
            return jsonify({'code': 400, 'msg': 'cant not find image by id {0}'.format(image_id)})
        if not target_images:
            return jsonify({'code': 400, 'msg': 'cant not find any image by group id {0}'.format(group_id)})
        # 3、比对features值
        sorted_matched_images = find_similar(image, target_images)
        result_body = []
        for matched in sorted_matched_images:
            oss_path = matched[2]
            expires = current_app.config['OSS_URL_EXPIRES']
            oss_url = get_oss_url(oss_path, expires)
            result_body.append({'id': matched[0], 'name': matched[1], 'url': oss_url, 'expires': expires})
        response = jsonify({'code': 200, 'data': result_body})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        return jsonify({'code': 500, 'error': "{0}".format(e)})


# 根据id获得图片url
@bp.route('<int:image_id>', methods=['GET'])
def get(image_id):
    try:
        if request.args.get('expires'):
            expires = int(request.args.get('expires'))
        else:
            expires = current_app.config['OSS_URL_EXPIRES']
        print(expires)

        if not image_id:
            return jsonify({'code': 400, 'msg': 'image_id is required.'})
        # 1、获得photo
        image = get_image(image_id)

        oss_url = get_oss_url(image[2], expires)
        if not image:
            return jsonify({'code': 400, 'msg': 'can not found image by id [{0}]'.format(image_id)})

        return jsonify(
            {'code': 200, 'oss_url': oss_url})
    except Exception as e:
        return jsonify({'code': 500, 'error': "{0}".format(e)})


# 删除图片
@bp.route('<int:image_id>', methods=['DELETE'])
def delete(image_id):
    try:
        if not image_id:
            return jsonify({'code': 400, 'msg': 'image_id is required.'})
        # 1、获得photo
        image = get_image(image_id)
        if not image:
            return jsonify({'code': 400, 'msg': 'can not found image by id [{0}]'.format(image_id)})

        # 2、获得该photo所在group的信息
        group = get_group(image[3])
        if not group:
            return jsonify({'code': 400, 'msg': 'can not found group by id [{0}]'.format(image[3])})

        oss_dir = group[1]
        oss_filename = '{0}{1}'.format(group[1], image[1])
        if not oss_dir.endswith("/"):
            oss_filename = '{0}{1}'.format(group[1], image[1])

        remove_file(oss_filename)

        delete_image(image_id)
        return jsonify(
            {'code': 200, 'msg': 'image [{0}] delete success'.format(image[1])})
    except Exception as e:
        return jsonify({'code': 500, 'error': "{0}".format(e)})
