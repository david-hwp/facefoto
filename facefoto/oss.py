from flask import (
    Blueprint, request, jsonify, current_app
)

from facefoto.oss_util import download_file, upload_file

bp = Blueprint('oss', __name__)


@bp.route('/download', methods=('GET', 'POST'))
def download():
    if request.method == 'POST':
        osspath = request.form['osspath']
        localpath = request.form['localpath']
        download_file(osspath, localpath)
        return jsonify(
            {'code': 200, 'msg': 'download file success.'})


@bp.route('/upload', methods=('GET', 'POST'))
def upload():
    if request.method == 'POST':
        osspath = request.form['osspath']
        localpath = request.form['localpath']
        oss_url = upload_file(osspath, localpath)
        return jsonify(
            {'code': 200, 'url': oss_url, 'url_express': current_app.config['OSS_URL_EXPIRES'],
             'msg': 'upload file success.'})
