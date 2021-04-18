import datetime
import os
import uuid

import flask
from flask import Flask, render_template, redirect, jsonify, request, Request, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import abort
from werkzeug.utils import secure_filename

from data import db_session
from data.add_event import AddEventForm
from data.edit_user import EditUserForm
from data.events import Events
from data.login_form import LoginForm
from data.users import User

from data.register import RegisterForm
from data.willcome import Willcome


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def create_new_folder(local_dir):
    newpath = local_dir
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    return newpath


MAX_CONTENT_LENGTH = 1024 * 1024

PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = '{}/static/img/'.format(PROJECT_HOME)

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['MAX_CONTENT_LENGTH'] = 16 * MAX_CONTENT_LENGTH
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
    today = str(datetime.date.today())
    if current_user.is_authenticated and current_user.moderator:
        events = db_sess.query(Events).filter(Events.date >= today).order_by(Events.date).all()
    else:

        events = db_sess.query(Events).filter(Events.is_moderated, Events.date >= today).order_by(Events.date).all()

    users = db_sess.query(User).all()
    names = {name.id: (name.surname, name.name) for name in users}
    return render_template("index.html", events=events, names=names, title='Эко акции')


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
            moderator=form.name.data == 'dasha_moderator'
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

        img = request.files['picture']
        filename = str(uuid.uuid4())
        img_name = "{}.{}".format(filename, secure_filename(img.filename))
        create_new_folder(app.config['UPLOAD_FOLDER'])
        saved_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)
        img.save(saved_path)

        events = Events(
            event=add_form.event.data,
            author=current_user.id,
            description=add_form.description.data,
            address=add_form.address.data,
            date=add_form.date.data,
            is_moderated=add_form.is_moderated.data,
            is_finished=False,
            picture=img_name
        )
        db_sess.add(events)
        db_sess.commit()
        return redirect('/')
    else:
        if request.method == "POST":
            print('не прошла валидация при добавлении')
    return render_template('addevent.html', title='Добавление нового события', form=add_form)


@app.route('/events/<int:id>', methods=['GET', 'POST'])
# @app.route('/events_delete/<int:id>', methods=['DELETE'])
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
            form.is_finished.data = events.is_finished
            form.picture = events.picture
        else:
            abort(404)
    # elif request.method == "DELETE":
    #     db_sess = db_session.create_session()
    #     events = db_sess.query(Events).filter(Events.id == id).first()
    #     if not events:
    #         abort(404)
    #     db_sess.delete(events)
    #     db_sess.commit()
    #     return redirect('/')

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
                events.is_finished = form.is_finished.data
            else:
                # events.is_moderated = False
                pass

            img = request.files['picture']
            if events.picture != img.filename:
                if str(events.picture) != '' and events.picture != None:
                    # картинка изменилась, сохраним новую под старым именем
                    img_name = events.picture
                else:
                    filename = str(uuid.uuid4())
                    img_name = "{}.{}".format(filename, secure_filename(img.filename))
                    events.picture = img_name

                create_new_folder(app.config['UPLOAD_FOLDER'])
                saved_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)
                img.save(saved_path)
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


@app.route('/events_delete/<int:id>', methods=['GET'])
@login_required
def delete_events(id):
    db_sess = db_session.create_session()
    events = db_sess.query(Events).filter(Events.id == id).first()
    if not events:
        abort(404)
    db_sess.delete(events)
    db_sess.commit()
    return redirect('/')


@app.route('/showevent/<int:id>', methods=['GET', 'POST'])
def showevent(id):
    if request.method == "GET":
        db_sess = db_session.create_session()
        events = db_sess.query(Events).filter(Events.id == id).first()
        if current_user.is_authenticated and current_user.moderator or events.is_moderated:
            pass
        else:
            abort(404)
        if current_user.is_authenticated:
            promise = bool(db_sess.query(Willcome).filter((Willcome.event_id == id),
                                                          (Willcome.user_id == current_user.id)).first())
        else:
            promise = False
        count = len(db_sess.query(Willcome).filter(Willcome.event_id == id).all())

    return render_template('show_event.html', title='Showing a event', event=events, promise=promise, count=count)


@app.route('/iwill/<int:id>', methods=['GET'])
@login_required
def iwill(id):
    if request.method == "GET":
        db_sess = db_session.create_session()
        events = db_sess.query(Events).filter(Events.id == id).first()
        if events:
            iwill = db_sess.query(Willcome).filter((Willcome.event_id == id),
                                                   (Willcome.user_id == current_user.id)).first()
            if not iwill:
                iwill = Willcome(
                    event_id=id,
                    user_id=current_user.id
                )
                db_sess.add(iwill)
                db_sess.commit()
            else:
                db_sess.delete(iwill)
                db_sess.commit()
    return redirect(url_for('showevent', id=id))


@app.route('/user/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    edit_form = EditUserForm

    if request.method == "GET":
        db_sess = db_session.create_session()
        user_info = db_sess.query(User).filter(User.id == id).first()
        if user_info:
            edit_form.surname.data = user_info.surname
            edit_form.name.data = user_info.name
            edit_form.age.data = user_info.age
            edit_form.address.data = user_info.address
            edit_form.moderator.data = user_info.moderator
            edit_form.email.data = user_info.email
        else:
            abort(404)

    elif request.method == "POST":
        pass
    # if edit_form.validate_on_submit():
    #     pass

    return render_template('edit_user.html', title='Информация о пользователе', form=edit_form, user_info=user_info)


def main():
    db_session.global_init("db/events.sqlite")

    app.run()


if __name__ == '__main__':
    # port = int(os.environ.get('PORT', 5000))
    # app.run(host='127.0.0.1', port=port)
    main()
