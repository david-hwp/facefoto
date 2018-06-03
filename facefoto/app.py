import os

from flask import Flask
from flask_uploads import UploadSet, IMAGES, configure_uploads


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY='facefoto',
        UPLOADED_PHOTOS_DEST=app.instance_path
        # store the database in the instance folder
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('application.cfg', silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register the database commands
    from facefoto import db
    db.init_app(app)
    app.config['UPLOADS_DEFAULT_DEST'] = app.instance_path+'/photos'
    photos = UploadSet('photos', IMAGES)
    configure_uploads(app, photos)

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # apply the blueprints to the app
    from facefoto import oss, groups, images
    # app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(oss.bp, url_prefix='/oss')
    app.register_blueprint(groups.bp, url_prefix='/groups')
    app.register_blueprint(images.bp, url_prefix='/images')
    # app.register_blueprint(blog.bp)

    # make url_for('index') == url_for('blog.index')
    # in another app, you might define a separate main index here with
    # app.route, while giving the blog blueprint a url_prefix, but for
    # the tutorial the blog will be the main index
    app.add_url_rule('/', endpoint='index')

    return app
