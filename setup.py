import io

from setuptools import find_packages, setup

with io.open('README.rst', 'rt', encoding='utf8') as f:
    readme = f.read()

setup(
    name='facefoto',
    version='1.0.0',
    url='http://facefoto.co',
    license='BSD',
    maintainer='hwp',
    maintainer_email='david_weiping@foxmail.com',
    description='The basic oss photo search project',
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask', 'click', 'werkzeug', 'pymysql', 'flask_uploads', 'oss2', 'numpy'
    ],
    extras_require={
        'test': [
            'pytest',
            'coverage',
        ],
    },
)
