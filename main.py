from flask import render_template
from flask_restful import Api
from app import create_app
from config import DevelopConfig,LocalConfig
from models import db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from urls import Url_register

#app = create_app(LocalConfig)
app = create_app(DevelopConfig)
# 注册路由
api = Api(app)
api.init_app(app)
Url_register(api)
@app.route('/')
def index():
    return render_template('index.html')
if __name__ == '__main__':
    manager = Manager(app)
    migrate = Migrate(app, db)
    manager.add_command('db', MigrateCommand)
    manager.run()
