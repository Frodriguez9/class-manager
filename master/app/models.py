from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
#from sqlalchemy import Column. String, create_engine
import json
import os

database_path = os.environ["DATABASE_URL"]

db = SQLAlchemy()
migrate = Migrate()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config['SQLALCHEMY_DATABASE_URI'] = database_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)
    migrate.init_app(app, db)


    #db.create_all()


'''
subject_student
    helper table:
        student --< student_subject >-- subject
'''
subject_student = db.Table('subject_student',
    db.Column('student_id', db.Integer, db.ForeignKey('people.id', ondelete='cascade', onupdate="cascade"),primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id', ondelete='cascade', onupdate="cascade"), primary_key=True)
)

'''
Subject
    Online class category - where students enroll
'''

class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String, nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    zoom_link = db.Column(db.String, nullable=False)
    students = db.relationship('Student',
                                secondary=subject_student,
                                lazy='joined',
                                backref=db.backref('courses', lazy='joined'))

    '''
    info()
        long form representation of the Subject model
    '''

    def info(self):
        return {
            'id': self.id,
            'category': self.category,
            'start': self.start,
            'zoom_link': self.zoom_link,
            'students': [student.info() for student in self.students]
        }

    '''
    insert()
        inserts a new model into a database
        EXAMPLE
            subject = Subject(category=req_title, start=req_dateTime,
                            zoom_link=req_link)
            subject.insert()
    '''

    def insert(self):
        db.session.add(self)
        db.session.commit()

    '''
    delete()
        deletes an existing model from the database
        the model must exist in the database
        EXAMPLE
            subject = Subject.query.filter(Subject.id == id).one_or_none()
            subject.delete()
    '''

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    '''
    update()
        updates a model from the database
        the model must exist in the database
        EXAMPLE
            subject = Subject.query.filter(Subject.id == id).one_or_none()
            subject.start = 2022-11-28 00:00:00
            subject.update()
    '''

    def update(self):
        db.session.commit()

    def __repr__(self):
        return f'<id: {self.id} category: {self.category}>'


'''
Student
    End users. People exploring online learning
'''
class Student(db.Model):
    __tablename__ = 'people'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)

    '''
    info()
        returns json representation of the Student model
    '''
    def info(self):
        return {
            "id": self.id,
            "name": self.name,
            "last_name": self.last_name
        }

    '''
    insert()
        inserts a new student into a database
        EXAMPLE
            student = Student(name=req_name, last_name=req_last_name)
            student.insert()
    '''

    def insert(self):
        db.session.add(self)
        db.session.commit()

    '''
    delete()
        Deletes an existing student from the database.
        The model must exist in the database
        EXAMPLE
            student = Student.query.filter(Student.id == id).one_or_none()
            student.delete()
    '''

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    '''
    update()
        updates a student info from the database
        the model must exist in the database
        EXAMPLE
            student = Student.query.filter(Student.id == id).one_or_none()
            student.name = "a differnt name"
            student.update()
    '''

    def update(self):
        db.session.commit()


    def __repr__(self):
        return f'<id: {self.id} last_name: {self.last_name}>'
