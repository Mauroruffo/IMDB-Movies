import operator
from crypt import methods
from operator import mod, itemgetter
from flask import Flask, request, redirect, render_template, url_for
from movies import models
import os
import csv

MoviesList = []
UserList = []

class csvConverter:
    @staticmethod
    def convert(MoviesList):
        with open("/src/movies/entrypoints/movie_results.csv", 'r') as file:
            csv_file = csv.DictReader(file)
            for row in csv_file:
                MoviesList.append(dict(row))
                #print(dict(row))
        return MoviesList

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    @staticmethod
    def generateMagicNumber(preferenceValue1, preferenceValue2, preferenceValue3, preferenceValue4, preferenceValue5):
        return mod((preferenceValue1 * preferenceValue2 * preferenceValue3 * preferenceValue4 * preferenceValue5), 5) + 1
    
    @staticmethod
    def saveUser(username, password, magicNumber):
        thisUser = {
        "username":username,
        "password":password,
        "preferenceKey": magicNumber
        }
        UserList.append(dict(thisUser))

# SRP solo se encarga de hacer el query filtrando por la llave de prefencia en orden desc #
# OCP ya que si se requiere un nuevo tipo de filtrado se puede crear una nueva clase #
class RecommendationsDefault:
    @staticmethod
    def generateTop10(MoviesListTop10, MoviesList, magic_Number):
        counter = 0
        for movie in MoviesList:
            if movie['preference_key'] == magic_Number and counter < 10:
                MoviesListTop10[counter] = dict(movie)
                counter = counter + 1
        return MoviesListTop10

# SRP solo se encarga de hacer el query filtrando por la llave de prefencia en orden desc #
class RecommendationsAsc:
    @staticmethod
    def generateLow10(MoviesListLow10, MoviesList, magic_Number):
        counter = 0
        for movie in reversed(MoviesList):
            if movie['preference_key'] == magic_Number and counter < 10:
                MoviesListLow10[counter] = dict(movie)
                counter = counter + 1
        return MoviesListLow10

# Dependency Inversion, para poder inicializar la lista de peliculas al cargar el programa #
class App:
    def __init__(self, converter: csvConverter):
        self.converter = converter

    def start(self):
        self.converter.convert(MoviesList)


newConverter = csvConverter()
newConverter.convert(MoviesList)

if __name__ == '__main__':
    converter = csvConverter()
    app = App(converter)
    app.start()

app = Flask(__name__, template_folder="/src/movies/entrypoints/")


@app.route("/hello", methods=["GET"])
def hello_world():
    return "Sam Raimi", 200

# Interface Segregated Principle, las rutas son separadas
@app.route('/', methods =["GET", "POST"])
# Facade Pattern, se usa la funcion gfg para poder interactuar con la informacion del usuario #
def register():
    if request.method == "POST":
       # getting input with name = username
       username = request.form.get("username")
       # getting input with password = password
       password = request.form.get("password")
       # getting input with checkbox
       preferenceValue1 = int(1 if request.form.get("value1") is None else request.form.get("value1"))
       preferenceValue2 = int(1 if request.form.get("value2") is None else request.form.get("value2"))
       preferenceValue3 = int(1 if request.form.get("value3") is None else request.form.get("value3"))
       preferenceValue4 = int(1 if request.form.get("value4") is None else request.form.get("value4"))
       preferenceValue5 = int(1 if request.form.get("value5") is None else request.form.get("value5"))

       newUser = User(username, password)
       magicNumber = newUser.generateMagicNumber(preferenceValue1, preferenceValue2, preferenceValue3, preferenceValue4, preferenceValue5)
       newUser.saveUser(username, password, magicNumber)
       
       return redirect(url_for('top10', name = username, magic_Number = magicNumber))
    return render_template("userRegister.html")

@app.route('/recommendations/<name>/<magic_Number>')
# Facade Pattern, se usa la funcion de top10 para poder generar los queries de los clientes #
# Chain of Reponsibility Pattern, la funcion actua top10 actua como handler recibiendo informacion de la funcion register y enviandolo al cliente html #
def top10(name, magic_Number):
    MoviesListTop10 = [None] * 10
    MoviesListLow10 = [None] * 10

    RecommendationsTop = RecommendationsDefault()
    RecommendationsLow = RecommendationsAsc()
    
    MoviesListTop10 = RecommendationsTop.generateTop10(MoviesListTop10, MoviesList, magic_Number)
    MoviesListLow10 = RecommendationsLow.generateLow10(MoviesListLow10, MoviesList, magic_Number)

    return render_template('show_all.html', username=name, magic_number=magic_Number, movielistTop = MoviesListTop10, movielistLow = MoviesListLow10)
