from flask import Blueprint, render_template

general_bp = Blueprint('general_bp', __name__,
    template_folder='templates')

@general_bp.route('/')
def index():
    return render_template('general/api_instructions.html')
