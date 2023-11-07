import os, re

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
    stocks = db.execute("SELECT symbol, name, price, SUM(shareNum) AS sharesTotal FROM transactions WHERE user_id = ? GROUP BY symbol", user_id)

    total = cash
    for stock in stocks:
        total += stock["sharesTotal"] * stock["price"]

    return render_template("index.html", stocks=stocks, cash=usd(cash), total=usd(total))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        stock = lookup(symbol)

        if not symbol:
            return apology ("missing symbol")
        elif not stock:
            return apology("invalid symbol")
        elif not (request.form.get("shares")).isdigit():
            return apology("cannot buy partial shares")

        shares = int(request.form.get("shares"))

        if shares <= 0:
            return apology("shares must be positive")

        user_id = session["user_id"]
        cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
        name = stock["name"]
        price = stock["price"]
        purchase = price * shares
        balance = cash - purchase

        if balance < 0:
            return apology('insufficient fund')
        else:
            flash("Bought!")
            db.execute("UPDATE users SET cash = ? WHERE id = ?", balance, user_id)
            db.execute("INSERT INTO transactions (user_id, symbol, name, price, shareNum, transactionType) VALUES (?, ?, ?, ?, ?, ?)", user_id, symbol, name, price, shares, "buy")
            return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    transactions = db.execute("SELECT symbol, shareNum, price, transactionType, transactionTime FROM transactions WHERE user_id = ?", user_id)
    return render_template("history.html", transactions = transactions)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()

        if not symbol:
            return apology("symbol not existed")

        stock = lookup(symbol)

        if not stock:
            return apology("invalid stock symbol")

        return render_template("quoted.html", stock=stock)

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("missing username")
        elif not password:
            return apology("missing password")
        elif not password:
            return apology("missing confirmed password")
        elif len(password) < 8:
            return apology("password has to be at least 8 letters")
        elif re.search("[a-zA-Z]", password) is None:
            return apology("password has to include at least one letter")
        elif re.search("[0-9]", password) is None:
            return apology("password has to include at least one number")
        elif re.search("[$&!]", password) is None:
            return apology("password has to include at least one special symbol $, & or !")
        elif password != confirmation:
            return apology("password not matched")

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(rows) != 0:
            return apology("username already exists")

        id = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password))

        session["user_id"]=id

        flash("Successfully registered!")

        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session["user_id"]
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))
        stock = lookup(symbol.upper())
        shares_owned = db.execute("SELECT shareNum FROM transactions WHERE user_id = ? AND symbol = ? GROUP BY symbol", user_id, symbol)[0]["shareNum"]

        if not shares or shares <= 0:
            return apology("shares must be a positive integer")
        elif shares > shares_owned:
            return apology ("not own enough shares")
        else:
            current_cash = db.execute("SELECT cash from users WHERE id =?", user_id)[0]["cash"]
            updated_cash = current_cash + shares * stock["price"]

            flash("Sold!")
            db.execute("UPDATE users SET cash = ? WHERE id = ?", updated_cash, user_id)
            db.execute("INSERT INTO transactions (user_id, symbol, name, price, shareNum, transactionType) VALUES (?, ?, ?, ?, ?, ?)", user_id, symbol, stock["name"], stock["price"], -shares, "sell")
            return redirect("/")
    else:
        symbols = db.execute("SELECT symbol FROM transactions WHERE user_id = ? GROUP BY symbol", user_id)
        return render_template("sell.html", symbols = symbols)