import json

import numpy
from flask import (
    current_app
)


def sort_by_value(d):
    items = d.items()
    backitems = [[v[1], v[0]] for v in items]
    backitems.sort(reverse=True)
    return [backitems[i][1] for i in range(0, len(backitems))]


# 计算两个特征值的欧式距离，此例中欧式距离最大值为2，距离越小，人像越相似
def get_euclidean_distance(src, target):
    v1 = numpy.array(src)
    v2 = numpy.array(target)
    dist = numpy.sqrt(numpy.sum(numpy.square(v1 - v2)))
    # print(dist)
    return dist


def find_similar(image, target_images):
    matched_images = {}
    limit = float(current_app.config['FEATURES_MAX_MATCH_LIMIT'])
    limit = 2 * (1 - limit)
    print("limit {0}".format(limit))
    body = json.loads(image[4])
    print("src image :{0}".format(image[1]))
    for b in body:
        features = b['features']
        for one in target_images:
            # print("target image :{0}".format(one[1]))
            one_body = json.loads(one[4])
            for one_b in one_body:
                one_features = one_b['features']
                dist = get_euclidean_distance(features, one_features)
                if dist < limit and image[1] != one[1]:
                    print("image match :{0}".format(one[1]))
                    matched_images[one] = dist
                    break
    return sort_by_value(matched_images)
    # print(sorted_matched_images)
