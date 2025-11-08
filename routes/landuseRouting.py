from flask import Blueprint
landuse_bp = Blueprint("landuse", __name__)

@landuse_bp.route('/landuse')
def landUsePage():
    return

@landuse_bp.route('/investments')
def investmentsPage():
    return