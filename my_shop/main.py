from datetime import datetime

from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy                       # импорт библиотеки которая позволяет работать с базами данных

from cloudipsp import Api, Checkout

app = Flask(__name__)                                         # создаем обьект фласк(передаем имя исполняемого файла)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'   # обращаемся к нашему приложению и его настройкам и какую настройку будем устанавливать по ключу и его значение
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)   # создаем обьект на основе sqlalchemy, присоеденяем ее к обьекту app
app.app_context().push()
"""Чтобы заработала команда db.create_all(), надо добавить строку 
app.app_context().push()
после строчки, где вы объявляете переменную db.
После выйти из консоли python, зайти в неё снова и опять прописать те команды"""
# БД - Таблицы - Записи
# Таблица:
# id    Название       Цена    Наличие      Описание
# 1  Alessio Nesca     5999    True       description
# 2  PIERRE CARDIN     8499    False      description
# 3  T.TACCARDI        3199    True       description


class Item(db.Model):
    """создание таблицы для базы данных"""
    id = db.Column(db.Integer, primary_key=True)      # будет первичным ключом
    title = db.Column(db.String(100), nullable=False) # строка не может быть пустой
    price = db.Column(db.Integer, nullable=False)
    # availability = db.Column(db.Boolean, default=False)# по умолчанию не будет в наличии
    description = db.Column(db.Text, nullable=True)
    availability = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return self.title


class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow,  onupdate=datetime.utcnow)

    def __repr__(self):
	    return "<{}:{}>".format(self.id, self.username)


#Главная страница
@app.route("/")            # делаем декоратор в которой отслеживаем главную страница
def index():
    items = Item.query.order_by(Item.price).all()  # скуэль запрос на сортировку по цене
    return render_template("index.html", data=items)


#Страница о нас
@app.route("/about")            # делаем декоратор в которой отслеживаем страницу о нас
def about():
    return render_template("about.html")


#Страница авторизации
@app.route('/login/', methods=['POST', 'GETt'])
def login():
    message = ''
    if request.method == 'POST':
        print(request.form)
        username = request.form.get('username')
        password = request.form.get('password')

        if username == 'root' and password == 'pass':
            message = "Correct username and password"
        else:
            message = "Wrong username or password"

    return render_template('login.html', message=message)


#Страница покупки
@app.route("/buy/<int:id>")
def item_buy(id):
    item = Item.query.get(id)
    api = Api(merchant_id=1396424,
              secret_key='test')
    checkout = Checkout(api=api)
    data = {
        "currency": "RUB",
        "amount": str(item.price) + "00" # добавляем копейки
    }
    url = checkout.url(data).get('checkout_url')
    return redirect(url)


#Страница всех продуктов
@app.route("/products")
def all_products():
    products = Item.query.order_by(Item.price).all()
    return render_template('products.html', products=products)


#Страница детализации продукта
@app.route("/products/<int:id>")
def product_detail(id):
    product = Item.query.get(id)
    return render_template('product_detail.html', product=product)


#Удаление продукта
@app.route("/products/<int:id>/delete")
def product_delete(id):
    product = Item.query.get_or_404(id)   # если такой записи в базе не будет, будет вызываться ошибка 404
    try:
        db.session.delete(product)
        db.session.commit()
        return redirect('/products')
    except:
        return "При удалении товара произошла ошибка"


#Редактирование продукта
@app.route("/products/<int:id>/update", methods=['POST', 'GET'])      # делаем декоратор для добавления информации в базу данных и отслеживаем метод GET и POST
def product_update(id):
    product = Item.query.get(id)
    if request.method == 'POST':
        product.title = request.form['title']
        product.price = request.form['price']
        product.availability = request.form['availability']
        product.description = request.form['description']
        try:
            db.session.commit()
            return redirect('/products')               # после добавления товара, переадресация на главную страницу
        except:
            return "что то пошло не так"
    else:
        return render_template("product_update.html", product=product)


#Создание продукта
@app.route("/create", methods=['POST', 'GET'])      # делаем декоратор для добавления информации в базу данных и отслеживаем метод GET и POST
def create():
    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']
        availability = request.form['availability']
        description = request.form['description']

        item = Item(title=title, price=price, availability=availability, description=description)

        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/products')               # после добавления товара, переадресация на главную страницу
        except:
            return "что то пошло не так"
    else:
        return render_template("create.html")


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)   # debug=True режим отладки(в котором видим различного рода ошибки), после релиза изменить на False