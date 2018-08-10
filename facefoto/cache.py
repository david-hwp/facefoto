from flask import (
    Blueprint, request,
    jsonify, current_app)

from facefoto.dao import *
from facefoto.oss_util import get_oss_url

bp = Blueprint('cache', __name__)

task_id = 0
head_group_id = None


# 根据user_id和group_id获得缓存结果
@bp.route('/search', methods=['GET'])
def search():
    try:
        user_id = request.args.get('user_id')
        group_id = request.args.get('group_id')
        if not user_id:
            return jsonify({'code': 400, 'msg': 'user_id is required.'})
        elif not group_id:
            return jsonify({'code': 400, 'msg': 'group_id is required.'})
        expires = current_app.config['OSS_URL_EXPIRES']
        caches = get_caches_by_user_id_and_group_id(user_id, group_id)
        data = []
        notified = []
        for cache in caches:
            notified.append(cache)
            photo = get_image(cache[3])
            oss_url = get_oss_url(photo[2], expires)
            one = {'user_id': cache[1], 'group_id': cache[2], 'image_id': cache[3], 'url': oss_url,
                   'url_express': expires}
            # start = now()
            data.append(one)
        return jsonify({'code': 200, 'data': data})

    except Exception as e:
        return jsonify({'code': 500, 'error': "{0}".format(e)})
