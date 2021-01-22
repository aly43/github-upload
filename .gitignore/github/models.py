from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False)
    pw_hash = db.Column(db.String(64), nullable=False)

    hosts = db.relationship('Event', backref='host', lazy='dynamic')
    # many-many relationship, people can attend many events and events have many attendees
    attends = db.relationship('Event', secondary='attends', backref=db.backref('events', lazy='dynamic'), lazy='dynamic')
    
    def __init__(self, username, pw_hash):
        self.username = username
        self.pw_hash = pw_hash

    def __repr__(self): # displays the user
        return '<User {}>'.format(self.username)

attends = db.Table('attends',
    db.Column('event_id', db.Integer, db.ForeignKey('event.event_id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.user_id'))
)

class Event(db.Model):
    event_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    #attendee_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    event_title = db.Column(db.String(32), nullable=False)
    descrip = db.Column(db.Text, nullable = False)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)

    #events = db.relationship('Events', backref='host')
    
    #attendees = db.relationship('Event', secondary='asst', primaryjoin='Event.event_id==asst.c.attendee_id', backref='attended_by', lazy='dynamic')

    def __init__(self, user_id, event_title, descrip, start_date, end_date):
        self.user_id = user_id
        self.event_title = event_title
        self.descrip = descrip
        self.start_date = start_date
        self.end_date = end_date

    def __repr__(self): # displays the event
        return '<Event {}>'.format(self.event_id)


#events = db.relationship('Events', backref='host')
# many-many relationship, people can attend many events and events have many attendees
#attends = db.relationship('User', secondary='asst', primaryjoin="User.user_id==asst.c.event_id", secondaryjoin='Event.event_id==asst.c.attendee_id', backref=db.backref=('attended_by', lazy='dynamic'), lazy='dynamic')
