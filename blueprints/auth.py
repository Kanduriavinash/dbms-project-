# blueprints/auth.py
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from extensions import db
from models import User
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

logger = logging.getLogger(__name__)


# ============================================================
# USER REGISTER
# ============================================================
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Customer registration.
    On success → flash animation → redirect to catalog.
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "danger")
            return redirect(url_for("auth.register"))

        # Pre-check uniqueness
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for("auth.register"))

        if email and User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return redirect(url_for("auth.register"))

        # Create user
        user = User(
            username=username,
            email=email or None,
            password_hash=generate_password_hash(password),
            role="customer"
        )
        db.session.add(user)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Username or email already exists.", "danger")
            return redirect(url_for("auth.register"))
        except Exception:
            db.session.rollback()
            flash("Unexpected error occurred.", "danger")
            logger.exception("Unexpected register error")
            return redirect(url_for("auth.register"))

        # Flash success and redirect
        flash("Account created! Redirecting…", "success")
        flash(url_for("catalog.catalog"), "success_redirect")
        return redirect(url_for("auth.register"))

    return render_template("auth/register.html", type="user")



# ============================================================
# ADMIN REGISTER
# ============================================================
@auth_bp.route("/register_admin", methods=["GET", "POST"])
def register_admin():
    """
    Admin registration.
    (Normally disabled in production.)
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "danger")
            return redirect(url_for("auth.register_admin"))

        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for("auth.register_admin"))

        if email and User.query.filter_by(email=email).first():
            flash("Email already exists.", "danger")
            return redirect(url_for("auth.register_admin"))

        user = User(
            username=username,
            email=email or None,
            password_hash=generate_password_hash(password),
            role="admin"
        )

        db.session.add(user)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Username or email already exists.", "danger")
            return redirect(url_for("auth.register_admin"))
        except Exception:
            db.session.rollback()
            flash("Unexpected error occurred.", "danger")
            logger.exception("Unexpected admin register error")
            return redirect(url_for("auth.register_admin"))

        flash("Admin account created! Redirecting…", "success")
        flash(url_for("auth.login_admin"), "success_redirect")
        return redirect(url_for("auth.register_admin"))

    return render_template("auth/register.html", type="admin")



# ============================================================
# USER LOGIN
# ============================================================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Customer login.
    → Merge guest cart into user cart if helper exists.
    → Redirect to catalog.
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password required.", "danger")
            return redirect(url_for("auth.login"))

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid username or password.", "danger")
            return redirect(url_for("auth.login"))

        # Login success
        login_user(user)

        # Try cart merge
        try:
            from blueprints.cart import merge_guest_cart_into_user
            try:
                merge_guest_cart_into_user(user.id)
            except Exception:
                logger.exception("Cart merge failed for user %s", user.id)
        except Exception:
            logger.debug("merge_guest_cart_into_user not available")

        flash("Signed in successfully!", "success")
        return redirect(url_for("catalog.catalog"))

    return render_template("auth/login.html", type="user")



# ============================================================
# ADMIN LOGIN
# ============================================================
@auth_bp.route("/login_admin", methods=["GET", "POST"])
def login_admin():
    """
    Admin login.
    Only role == 'admin' allowed.
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password required.", "danger")
            return redirect(url_for("auth.login_admin"))

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, password) or user.role != "admin":
            flash("Invalid admin credentials.", "danger")
            return redirect(url_for("auth.login_admin"))

        login_user(user)

        # Try merging guest cart
        try:
            from blueprints.cart import merge_guest_cart_into_user
            try:
                merge_guest_cart_into_user(user.id)
            except Exception:
                logger.exception("Cart merge failed for admin %s", user.id)
        except Exception:
            logger.debug("merge_guest_cart_into_user not available")

        flash("Admin login successful!", "success")

        # Admin dashboard
        try:
            return redirect(url_for("admin.dashboard"))
        except Exception:
            return redirect(url_for("catalog.catalog"))

    return render_template("auth/login.html", type="admin")



# ============================================================
# LOGOUT
# ============================================================
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    try:
        return redirect(url_for("index"))
    except Exception:
        return redirect(url_for("auth.register"))
