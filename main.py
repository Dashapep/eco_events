import datetime
import flask
from flask import Flask, render_template, redirect, jsonify, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import abort

from data import db_session
from data.add_event import AddEventForm
from data.login_form import LoginForm
from data.users import User
from data.events import Events
from data.register import RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
blueprint = flask.Blueprint(
    'events_api',
    __name__,
    template_folder='templates'
)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Wrong login or password", form=form)
    return render_template('login.html', title='Authorization', form=form)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated and current_user.moderator:
        events = db_sess.query(Events).all()
    else:
        events = db_sess.query(Events).filter(Events.is_moderated)
    users = db_sess.query(User).all()
    names = {name.id: (name.surname, name.name) for name in users}
    return render_template("index.html", events=events, names=names, title='Event log')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Register', form=form,
                                   message="Passwords don't match")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Register', form=form,
                                   message="This user already exists")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            age=form.age.data,
            email=form.email.data,
            speciality=form.speciality.data,
            address=form.address.data,
            moderator=form.name.data=='dasha_moderator'
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/addevent', methods=['GET', 'POST'])
def addevent():
    add_form = AddEventForm()
    if add_form.validate_on_submit():
        db_sess = db_session.create_session()
        events = Events(
            event=add_form.event.data,
            # author=current_user.id,
            description=add_form.description.data,
            address=add_form.address.data,
            # date=datetime.datetime.now(),
            date=add_form.date.data,
            is_finished=False)
        db_sess.add(events)
        db_sess.commit()
        return redirect('/')
    else:
        print('не прошла валидация при добавлении')
    return render_template('addevent.html', title='Adding a event', form=add_form)

@app.route('/events/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_events(id):
    form = AddEventForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        events = db_sess.query(Events).filter(Events.id == id).first()
        if events:
            form.event.data = events.event
            form.description.data = events.description
            form.date.data = events.date
            form.address.data = events.address
            form.is_moderated.data = events.is_moderated
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        events = db_sess.query(Events).filter(Events.id == id).first()
        if events:
            events.event = form.event.data
            events.description = form.description.data
            events.date = form.date.data
            events.address = form.address.data
            if current_user.is_authenticated and current_user.moderator:
                events.is_moderated = form.is_moderated.data
            else:
                events.is_moderated = False
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)

    else:
        print('не прошла валидация формы')
    return render_template('addevent.html',
                           title='Редактирование события',
                           form=form
                           )

@app.route('/showevent/<int:id>', methods=['GET', 'POST'])
def showevent(id):
    if request.method == "GET":
        db_sess = db_session.create_session()
        events = db_sess.query(Events).filter(Events.id == id).first()
        if not events.is_moderated:
            abort(404)
    return render_template('show_event.html', title='Showing a event', event=events)


def main():
    db_session.global_init("db/events.sqlite")

    app.run()


if __name__ == '__main__':
    main()
