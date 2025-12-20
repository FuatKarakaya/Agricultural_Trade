from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from database import fetch_query

auth_bp = Blueprint("auth", __name__)

# ====== DECORATOR'LAR ======

def login_required(f):
    """Giriş yapan herkes (user + admin) erişebilir"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash("Bu sayfaya erişmek için giriş yapmalısınız.", "error")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Only admin users can access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash("Please log in to access this page.", "error")
            return redirect(url_for('auth.login'))
        
        if not session.get('is_admin'):
            flash("Admin privileges are required for this operation.", "error")
            return redirect(request.referrer or url_for('main.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

# Public route'lara decorator koymaya gerek yok, zaten herkese açık


# ====== LOGIN/LOGOUT ROUTES ======

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash("Kullanıcı adı ve şifre gerekli.", "error")
            return render_template('login.html')
        
        user = fetch_query(
            "SELECT user_id, username, password, is_admin FROM Users WHERE username = %s;",
            (username,)
        )
        
        if not user:
            flash("Kullanıcı adı veya şifre hatalı.", "error")
            return render_template('login.html')
        
        user = user[0]
        
        if user['password'] == password:
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            session['logged_in'] = True
            
            if user['is_admin']:
                flash(f"Hoş geldiniz, Admin {user['username']}!", "success")
            else:
                flash(f"Hoş geldiniz, {user['username']}!", "success")
            
            return redirect('/')
        else:
            flash("Kullanıcı adı veya şifre hatalı.", "error")
            return render_template('login.html')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    username = session.get('username', 'Kullanıcı')
    session.clear()
    flash(f"{username}, başarıyla çıkış yaptınız.", "success")
    return redirect(url_for('auth.login'))