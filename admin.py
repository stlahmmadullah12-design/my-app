import os
from flask import Blueprint, request, redirect, session
from database import get_connection

admin = Blueprint("admin", __name__, url_prefix="/admin")

@admin.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if (print("USERNAME SET:", bool(os.getenv("ADMIN_USERNAME")))
print("PASSWORD SET:", bool(os.getenv("ADMIN_PASSWORD")))
            request.form.get("username") == os.getenv("ADMIN_USERNAME")
            and request.form.get("password") == os.getenv("ADMIN_PASSWORD")
        ):
            session["admin"] = True
            return redirect("/admin/dashboard")

    return """
    <h2>Salman Premium Store Admin</h2>
    <form method="post">
    <input name="username" placeholder="Username" required>
    <input name="password" type="password" placeholder="Password" required>
    <button type="submit">Login</button>
    </form>
    """

@admin.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect("/admin/")

    return """
    <h1>Admin Dashboard</h1>
    <p><a href="/admin/products">Manage Products</a></p>
    """

@admin.route("/products", methods=["GET", "POST"])
def products():
    if not session.get("admin"):
        return redirect("/admin/")

    message = ""

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()

        try:
            price = float(request.form.get("price", ""))
            stock = int(request.form.get("stock", ""))
            if not name or price < 0 or stock < 0:
                raise ValueError

            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """INSERT INTO products
                        (name, description, price, stock)
                        VALUES (%s, %s, %s, %s)""",
                        (name, description, price, stock)
                    )
                conn.commit()

            message = "Product added successfully!"
        except (ValueError, TypeError):
            message = "Please enter valid product information."

    return f"""
    <h1>Manage Products</h1>
    <p>{message}</p>
    <form method="post">
    <input name="name" placeholder="Product Name" required><br>
    <textarea name="description" placeholder="Description"></textarea><br>
    <input name="price" type="number" min="0" step="0.01"
    placeholder="Price" required><br>
    <input name="stock" type="number" min="0"
    placeholder="Stock" required><br>
    <button type="submit">Add Product</button>
    </form>
    <p><a href="/admin/dashboard">Dashboard</a></p>
    """
    
def register_admin(app):
    app.secret_key = os.getenv("SECRET_KEY")
    if not app.secret_key:
        raise RuntimeError("SECRET_KEY is not configured")
    app.register_blueprint(admin)

