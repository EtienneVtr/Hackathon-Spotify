from crypt import METHOD_BLOWFISH
from typing import ContextManager
from flask import Flask, render_template, g, request, redirect, url_for, session
import sqlite3

import random

DATABASE = 'base_de_données/database.db'
app = Flask(__name__)
app.secret_key = "HACKATHON "
app.config['SECRET_KEY'] = "HACKATHON "

@app.route('/', methods=['GET', 'POST'])
def acceuil_projet():
    return render_template('acceuil_projet.html')

if __name__ == '__main__':
    app.run()
