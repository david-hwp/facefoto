# -*- coding: utf-8 -*-

import os
import shutil

import oss2
from flask import current_app, g


def get_bucket():
    if 'bucket' not in g:
        g.bucket = oss2.Bucket(oss2.Auth(
            current_app.config['ACCESS_KEY_ID'],
            current_app.config['ACCESS_KEY_SECRET']),
            current_app.config['ENDPOINT'],
            current_app.config['BUCKET_NAME']
        )
    return g.bucket


def download_file(osspath, localpath):
    bucket = get_bucket()
    try:
        os.path.join(localpath)
    except OSError:
        pass
    with open(oss2.to_unicode(localpath), 'wb') as f:
        shutil.copyfileobj(bucket.get_object(osspath), f)


def upload_file(osspath, localpath):
    bucket = get_bucket()
    bucket.put_object_from_file(osspath, localpath)
    return get_oss_url(osspath, current_app.config['OSS_URL_EXPIRES'])


def remove_file(osspath):
    bucket = get_bucket()
    bucket.delete_object(osspath)


def get_oss_url(osspath, expries):
    bucket = get_bucket()
    return bucket.sign_url('GET', osspath, expries)
