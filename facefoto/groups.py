from flask import (
    Blueprint, request, jsonify
)

from facefoto.db import get_db

bp = Blueprint('groups', __name__)


def get_group_by_dir(dir):
    """Get a post and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM `group` WHERE oss_dir = %s', dir)
    group = cursor.fetchone()

    # if group is None:
    #     abort(404, "group{0} doesn't exist.".format(dir))

    return group


def get_group(id):
    """Get a post and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM `group` WHERE id = %s', id)
    group = cursor.fetchone()

    # if group is None:
    #     abort(404, "group{0} doesn't exist.".format(dir))

    return group


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

            db = get_db()
            cursor = db.cursor()
            cursor.execute('INSERT INTO `group`(oss_dir) VALUES ("%s")' % oss_dir)
            group_id = cursor.lastrowid
            db.commit()
            return jsonify({'code': 200, 'group_id': group_id, 'msg': 'group [{0}] create success'.format(oss_dir)})
        except Exception as e:
            return jsonify({'code': 500, 'error': "{0}".format(e)})


@bp.route('/<int:id>', methods=['PUT'])
def update(id):
    """Update a group """
    if request.method == 'PUT':
        oss_dir = request.form['oss_dir']
        if not oss_dir:
            return jsonify({'code': 400, 'msg': 'oss_dir is required.'})

        try:
            group = get_group(id)
            if not group:
                return jsonify({'code': 400, 'msg': 'can not found group by id [{0}]'.format(id)})
            else:
                db = get_db()
                db.cursor().execute('UPDATE `group` SET oss_dir = "%s"  WHERE id = "%d"' % (oss_dir, id))
                db.commit()
                return jsonify(
                    {'code': 200, 'msg': 'group [{0}] success update to [{1}]'.format(id, oss_dir)})
        except Exception as e:
            return jsonify({'code': 500, 'error': '{0}'.format(e)})


@bp.route('/count/<int:id>', methods=['GET'])
def count(id):
    """Update a group """
    if request.method == 'GET':
        try:
            group = get_group(id)
            if not group:
                return jsonify({'code': 400, 'msg': 'can not found group by id [{0}]'.format(id)})
            else:
                db = get_db()
                cursor = db.cursor()
                cursor.execute('SELECT COUNT(*) FROM `photo` WHERE group_id = %s', id)
                result = cursor.fetchone()
                return jsonify(
                    {'code': 200, 'msg': 'query success', 'result': result[0]})
        except Exception as e:
            return jsonify({'code': 500, 'error': '{0}'.format(e)})


@bp.route('/<int:id>', methods=['DELETE'])
# @login_required
def delete(id):
    """Delete a group."""
    try:
        group = get_group(id)
        if not group:
            return jsonify({'code': 400, 'msg': 'can not found group by id [{0}]'.format(id)})

        db = get_db()
        db.cursor().execute('DELETE FROM `group` WHERE id = "%d"' % id)
        db.commit()
        return jsonify(
            {'code': 200, 'msg': 'group [{0}] delete success'.format(group[1])})
    except Exception as e:
        return jsonify({'code': 500, 'error': "{0}".format(e)})
