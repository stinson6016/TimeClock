
def load_blueprints(app):
    # load blueprints
    from .main import main
    from .records.records import records
    from .clock.clock import clock
    from .setup.setup import setup

    # register blueprints
    app.register_blueprint(main, url_prefix='/')
    app.register_blueprint(records, url_prefix='/records')
    app.register_blueprint(clock, url_prefix='/clock')
    app.register_blueprint(setup, url_prefix='/setup')