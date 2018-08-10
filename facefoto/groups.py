from flask import (
    Blueprint, request, jsonify
)
from facefoto.dao import *
bp = Blueprint('groups', __name__)


@bp.route('', methods=['POST'])
def create():
    """Create a new group"""
    if request.method == 'POST':
        oss_dir = request.form['oss_dir']

        if not oss_dir:
            return jsonify({'code': 400, 'msg': 'oss_dir is required.'})
        if oss_dir.startswith("/"):
            return jsonify({'code': 400, 'msg': "oss_dir can not start with '/'"})

        try:
            group = get_group_by_dir(oss_dir)
            if group:
                return jsonify(
                    {'code': 400, 'group_id': group[0], 'msg': 'group [{0}] already created'.format(oss_dir)})
            group_id = add_group(oss_dir)
            return jsonify({'code': 200, 'group_id': group_id, 'msg': 'group [{0}] create success'.format(oss_dir)})
        except Exception as e:
            return jsonify({'code': 500, 'error': "{0}".format(e)})


@bp.route('/<int:_id>', methods=['PUT'])
def update(_id):
    """Update a group """
    if request.method == 'PUT':
        oss_dir = request.form['oss_dir']
        if not oss_dir:
            return jsonify({'code': 400, 'msg': 'oss_dir is required.'})

        try:
            group = get_group(_id)
            if not group:
                return jsonify({'code': 400, 'msg': 'can not found group by id [{0}]'.format(_id)})
            else:
                update_group(oss_dir, _id)
                return jsonify(
                    {'code': 200, 'msg': 'group [{0}] success update to [{1}]'.format(_id, oss_dir)})
        except Exception as e:
            return jsonify({'code': 500, 'error': '{0}'.format(e)})


@bp.route('/count/<int:_id>', methods=['GET'])
def count(_id):
    """Update a group """
    if request.method == 'GET':
        try:
            group = get_group(_id)
            if not group:
                return jsonify({'code': 400, 'msg': 'can not found group by id [{0}]'.format(_id)})
            else:
                result = count_group(_id)
                return jsonify(
                    {'code': 200, 'msg': 'query success', 'result': result[0]})
        except Exception as e:
            return jsonify({'code': 500, 'error': '{0}'.format(e)})


@bp.route('/<int:_id>', methods=['DELETE'])
# @login_required
def delete(_id):
    """Delete a group."""
    try:
        group = get_group(_id)
        if not group:
            return jsonify({'code': 400, 'msg': 'can not found group by id [{0}]'.format(_id)})
        delete_group(_id)
        return jsonify(
            {'code': 200, 'msg': 'group [{0}] delete success'.format(group[1])})
    except Exception as e:
        return jsonify({'code': 500, 'error': "{0}".format(e)})
