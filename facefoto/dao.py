from facefoto.db import MyPymysqlPool


def add_group(oss_dir):
    db = MyPymysqlPool()
    sql = "INSERT INTO `group` (oss_dir) VALUES (%s)"
    result = db.insert(sql, oss_dir)
    db.dispose()
    return result


def get_group(_id):
    db = MyPymysqlPool()
    sql = "SELECT * FROM `group` WHERE id = %s"
    result = db.getOne(sql, _id)
    db.dispose()
    return result


def get_group_by_dir(_dir):
    db = MyPymysqlPool()
    sql = "SELECT * FROM `group` WHERE oss_dir = %s"
    result = db.getOne(sql, _dir)
    db.dispose()
    return result


def update_group(oss_dir, _id):
    db = MyPymysqlPool()
    sql = "UPDATE `group` SET oss_dir = %s WHERE id = %s"
    result = db.update(sql, (oss_dir, _id))
    db.dispose()
    return result


def count_group(_id):
    db = MyPymysqlPool()
    sql = "SELECT COUNT(*) FROM `photo` WHERE group_id = %s"
    result = db.getOne(sql, _id)
    db.dispose()
    return result


def delete_group(_id):
    db = MyPymysqlPool()
    sql = "DELETE FROM `group` WHERE id = %s"
    result = db.delete(sql, _id)
    db.dispose()
    return result


def add_image(name, oss_path, group_id, feature):
    db = MyPymysqlPool()
    sql = "insert into `photo` (name, oss_path, group_id, feature) VALUES (%s,%s,%s,%s)"
    result = db.insert(sql, (name, oss_path, group_id, feature))
    db.dispose()
    return result


def get_image(_id):
    db = MyPymysqlPool()
    sql = "SELECT * FROM `photo` where id=%s"
    result = db.getOne(sql, _id)
    db.dispose()
    return result


def get_images_by_group_id(group_id):
    db = MyPymysqlPool()
    sql = "SELECT * FROM `photo` where group_id=%s"
    result = db.getAll(sql, group_id)
    db.dispose()
    return result


def get_image_by_oss_path(oss_path):
    db = MyPymysqlPool()
    sql = "SELECT * FROM `photo` where oss_path like '%%%s'" % oss_path
    result = db.getOne(sql)
    db.dispose()
    return result


def get_image_by_muiti_condition(filename, oss_filename, head_group_id):
    db = MyPymysqlPool()
    sql = "select id from `photo` where name=%s and oss_path=%s and group_id =%s"
    result = db.getOne(sql, (filename, oss_filename, head_group_id))
    db.dispose()
    return result


def delete_image_by_oss_path(oss_path):
    db = MyPymysqlPool()
    sql = "DELETE FROM `photo` where oss_path=%s"
    result = db.delete(sql, oss_path)
    db.dispose()
    return result


def update_image(name, oss_path, group_id, feature, _id):
    db = MyPymysqlPool()
    sql = "update `photo` set name=%s, oss_path=%s, group_id=%s, feature=%s where `id` = %s"
    result = db.update(sql, (name, oss_path, group_id, feature, _id))
    db.dispose()
    return result


def delete_image(_id):
    db = MyPymysqlPool()
    sql = "DELETE FROM `photo` where id=%s"
    result = db.delete(sql, _id)
    db.dispose()
    return result


def add_face(user_id, group_id, photo_id):
    db = MyPymysqlPool()
    sql = "insert into `face` (user_id, group_id, photo_id) VALUES (%s,%s,%s)"
    result = db.insert(sql, (user_id, group_id, photo_id))
    db.dispose()
    return result


def get_face_by_user_id_and_grou_id(user_id, group_id):
    db = MyPymysqlPool()
    sql = "select id from `face` where user_id=%s and group_id =%s"
    result = db.getOne(sql, (user_id, group_id))
    db.dispose()
    return result


def get_face_by_photo_id(photo_id):
    db = MyPymysqlPool()
    sql = "select id from `face` where photo_id=%s"
    result = db.getOne(sql, photo_id)
    db.dispose()
    return result


def get_faces_by_group_id(group_id):
    db = MyPymysqlPool()
    sql = "select * from `face` where group_id=%s"
    result = db.getAll(sql, group_id)
    db.dispose()
    return result


def update_face(user_id, group_id, photo_id, face_id):
    db = MyPymysqlPool()
    sql = "update `face` set user_id=%s, group_id=%s, photo_id=%s where `id`=%s"
    result = db.insert(sql, (user_id, group_id, photo_id, face_id))
    db.dispose()
    return result


def add_cache(user_id, group_id, photo_id):
    db = MyPymysqlPool()
    sql = "insert into `cache` (user_id, group_id, similar_photo_id ,notified) value (%s,%s,%s,false)"
    result = db.insert(sql, (user_id, group_id, photo_id))
    db.dispose()
    return result


def add_or_update_cache(user_id, group_id, photo_id):
    cache = get_cache_by_muti_condition(user_id, group_id, photo_id)
    if cache:
        # TODO 测试完毕后去掉return
        return update_cache(user_id, group_id, photo_id, False, cache[0])
    else:
        return add_cache(user_id, group_id, photo_id)


def update_cache(user_id, group_id, photo_id, notified, _id):
    db = MyPymysqlPool()
    sql = "update `cache` set user_id=%s, group_id=%s, similar_photo_id=%s, notified=%s where `id`=%s"
    db.update(sql, (user_id, group_id, photo_id, notified, _id))
    db.dispose()
    return _id


def get_cache(_id):
    db = MyPymysqlPool()
    sql = "select * from `cache` where id=%s"
    result = db.getOne(sql, _id)
    db.dispose()
    return result


def get_caches_by_user_id_and_group_id(user_id, group_id):
    db = MyPymysqlPool()
    sql = "select * from `cache` where user_id=%s and group_id=%s"
    result = db.getAll(sql, (user_id, group_id))
    db.dispose()
    return result


def get_cache_by_muti_condition(user_id, group_id, photo_id):
    db = MyPymysqlPool()
    sql = "select * from `cache` where user_id=%s and group_id=%s and similar_photo_id=%s"
    result = db.getOne(sql, (user_id, group_id, photo_id))
    db.dispose()
    return result
