import time
from flask import (
    Blueprint, request,
    jsonify)

bp = Blueprint('notify_client', __name__)

task_id = 0
head_group_id = None


# 通知接口
@bp.route('', methods=['POST'])
def notify():
    data = request.get_json()
    print(data)
    time.sleep(10)
    return jsonify({"code": 200, "msg": "ok"})
