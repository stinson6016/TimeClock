from flask import Flask

def load_blueprints(app: Flask) -> None:
    '''Moved loading blueprints to another file to make editing easier'''
    # load blueprints
    from .main import main
    from .records.records import records
    from .clock.clock import clock
    from .setup.setup import setup

    # register blueprints
    app.register_blueprint(main)
    app.register_blueprint(records)
    app.register_blueprint(clock)
    app.register_blueprint(setup)