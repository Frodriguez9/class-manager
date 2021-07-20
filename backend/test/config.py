import unittest
from unittest.mock import patch
import json
from flask_sqlalchemy import SQLAlchemy

from backend.app.app import create_app
from backend.app.models import setup_db, subject_student, Subject, Student
from backend.app.functions import query_a_record
