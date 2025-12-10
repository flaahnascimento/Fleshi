from appfleshi import db, app
from appfleshi.models import Photo, User

with app.app_context():
    db.create_all()