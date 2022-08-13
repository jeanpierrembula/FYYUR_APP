import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
dialect = 'postgresql'
utilisateur = 'postgres'
mot_de_pass = 'admin'
adresse = 'localhost'
port = '5432'
base_de_donnee = 'fyyurapp'


# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(dialect, utilisateur, mot_de_pass, adresse, port, base_de_donnee)

SQLALCHEMY_TRACK_MODIFICATIONS = False
