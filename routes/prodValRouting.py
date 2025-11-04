from flask import Blueprint, render_template, request
from database import execute_query

prod_val_bp = Blueprint("prod_val", __name__)
