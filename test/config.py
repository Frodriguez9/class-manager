import unittest
from unittest.mock import patch
import json
from flask_sqlalchemy import SQLAlchemy

from app.app import create_app
from app.models import setup_db, subject_student, Subject, Student
from app.functions import query_a_record
