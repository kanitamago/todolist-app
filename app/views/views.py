from app import app
from flask import request, redirect, url_for, render_template, flash, session
from werkzeug import secure_filename
from app import db
from app.models.todo_items import Todo_item
from app.models.flag_db import Flag
from app.models.admin import Admin
import os
import numpy as np
from datetime import datetime

def random_maker(k):
    if k:
        fight_image = os.listdir("app/static/uploads/fight")
        clear_image = os.listdir("app/static/uploads/clear")
        fight_comments = Admin.query.order_by(Admin.id.desc()).all()
        final_fight = []
        for item in fight_comments:
            if item.fight_word != None:
                final_fight.append(item.fight_word)
            else:
                continue
        clear_comments = Admin.query.order_by(Admin.id.desc()).all()
        final_clear = []
        for item in clear_comments:
            if item.clear_word != None:
                final_clear.append(item.clear_word)
            else:
                continue
        if fight_image:
            fightImage_weight = [(1 / len(fight_image))] * len(fight_image)
            fight_images = np.random.choice(fight_image, size=k, p=fightImage_weight)
        else:
            fight_images = [None] * k
        if clear_image:
            clearImage_weight = [(1 / len(clear_image))] * len(clear_image)
            clear_images = np.random.choice(clear_image, size=k, p=clearImage_weight)
        else:
            clear_images = [None] * k
        if final_fight:
            fightWord_weight = [(1 / len(final_fight))] * len(final_fight)
            fight_words = np.random.choice(final_fight, size=k, p=fightWord_weight)
        else:
            fight_words = ["FIGHT!!!"] * k
        if final_clear:
            clearWord_weight = [(1 / len(final_clear))] * len(final_clear)
            clear_words = np.random.choice(final_clear, size=k, p=clearWord_weight)
        else:
            clear_words = ["CLEAR!!!"] * k
        return [fight_images, clear_images, fight_words, clear_words]
    else:
        return None

def login_required(view):
    @wraps(view)
    def inner(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    return inner

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form["username"] != app.config["USERNAME"]:
            flash("ログイン失敗")
            return render_template("login.html", error_username="ユーザー名が異なります", error_password="もう一度入力してください")
        elif request.form["password"] != app.config["PASSWORD"]:
            flash("ログイン失敗")
            return render_template("login.html", correct_username=request.form["username"], error_password="パスワードが異なります")
        else:
            session["logged_in"] = True
            flash("ログインしました")
            return redirect(url_for("admin"))
    #GET method(Access URL or Click Button)
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    flash("ログアウトしました")
    return redirect(url_for("index"))

@app.route("/")
def index():
    todo_items = Todo_item.query.order_by(Todo_item.id.desc()).all()
    clear_items = Flag.query.order_by(Flag.item_id.desc()).all()
    fight_set = random_maker(len(todo_items))
    if fight_set:
        return render_template("index.html", todo_items=zip(todo_items, clear_items, fight_set[0], fight_set[1], fight_set[2], fight_set[3]))
    else:
        return render_template("index.html", todo_items=None)

@app.route("/create")
def show_createTodo():
    return render_template("create_todo.html")


@app.route("/create/post", methods=["POST"])
def create_todo():
    text = request.form["text"]
    text = text.replace("　", " ")
    text = text.split("　")
    text = text[0].replace("\r\n", "<br>")
    if text == "":
        flash("内容がありません")
        return redirect(url_for("index"))
    todo_item = Todo_item(text=text)
    clear_item = Flag(item_id=todo_item.id)
    db.session.add(todo_item)
    db.session.commit()
    db.session.add(clear_item)
    db.session.commit()
    flash("Todoリストを追加しました")
    return redirect(url_for("index"))

@app.route("/<int:id>", methods=["GET"])
def detail(id):
    clear_image = os.listdir("app/static/uploads/clear")
    clearImage_weight = [(1 / len(clear_image))] * len(clear_image)
    image = np.random.choice(clear_image, size=1, p=clearImage_weight)
    todo_item = Todo_item.query.get(id)
    clear_item = Flag.query.get(id)
    return render_template("detail.html", todo_item=todo_item, clear_item=clear_item, image=image[0])

@app.route("/<int:id>/delete", methods=["POST"])
def delete(id):
    todo_item = Todo_item.query.get(id)
    clear_item = Flag.query.get(id)
    db.session.delete(todo_item)
    db.session.commit()
    db.session.delete(clear_item)
    db.session.commit()
    flash("Todoリストを削除しました")
    return redirect(url_for("index"))

@app.route("/<int:id>/clear", methods=["POST"])
def clear(id):
    clear_item = Flag.query.get(id)
    clear_item.clear_flag = 1
    clear_item.clear_at = "{0:%Y/%m/%d/ %H:%M:%S}".format(datetime.now())
    db.session.merge(clear_item)
    db.session.commit()
    flash("オールクリア")
    return redirect(url_for("index"))

#-------------------------------------------------------------------------------
#管理者画面

UPLOAD_FOLDER_FIGHT = 'app/static/uploads/fight'
UPLOAD_FOLDER_CLEAR = 'app/static/uploads/clear'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

@app.route("/admin", methods=["GET"])
def admin():
    return render_template("admin.html")

def create_name(filename, flag):
    fight_images = os.listdir("app/static/uploads/fight")
    clear_images = os.listdir("app/static/uploads/clear")
    if flag == "FIGHT":
        max_num1 = max([int(image_num[-5]) for image_num in fight_images])
        max_num1 += 1
        max_num2 = [image_num[-6:-4] for image_num in fight_images]
        max_num3 = []
        for num in max_num2:
            try:
                num = int(num)
                max_num3.append(num)
            except:
                continue
        if not max_num3:
            name = filename.lower()
            name = "fight_img" + str(max_num1) + name[-4:]
        else:
            max_num4 = max(max_num3)
            max_num4 += 1
            name = filename.lower()
            name = "fight_img" + str(max_num4) + name[-4:]
    elif flag == "CLEAR":
        max_num1 = max([int(image_num[-5]) for image_num in clear_images])
        max_num1 += 1
        max_num2 = [image_num[-6:-4] for image_num in clear_images]
        max_num3 = []
        for num in max_num2:
            try:
                num = int(num)
                max_num3.append(num)
            except:
                continue
        if not max_num3:
            name = filename.lower()
            name = "clear_img" + str(max_num1) + name[-4:]
        else:
            max_num4 = max(max_num3)
            max_num4 += 1
            name = filename.lower()
            name = "clear_img" + str(max_num4) + name[-4:]
    return name

def allowed_file(filename):
    global ALLOWED_EXTENSIONS
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/uploads/fight', methods=['POST'])
def fight_upload():
    global UPLOAD_FOLDER_FIGHT
    flag = "FIGHT"
    if request.method == 'POST':
        file = request.files['image']
        filename = create_name(file.filename, flag)
        print(filename)
        if file and allowed_file(filename):
            filename = secure_filename(filename)
            file.save(os.path.join(UPLOAD_FOLDER_FIGHT, filename))
            flash("応援画像を保存しました")
    return redirect(url_for("admin"))

@app.route('/uploads/clear', methods=['POST'])
def clear_upload():
    global UPLOAD_FOLDER_CLEAR
    flag = "CLEAR"
    if request.method == 'POST':
        file = request.files['image']
        filename = create_name(file.filename, flag)
        print(filename)
        if file and allowed_file(filename):
            filename = secure_filename(filename)
            file.save(os.path.join(UPLOAD_FOLDER_CLEAR, filename))
            flash("お疲れ様画像を保存しました")
    return redirect(url_for("admin"))

@app.route("/input/fight", methods=["POST"])
def fight_comment():
    comment = request.form["fight_text"]
    fight_db = Admin(fight_word=comment)
    db.session.add(fight_db)
    db.session.commit()
    flash("応援コメントを保存しました")
    return redirect(url_for("admin"))

@app.route("/input/clear", methods=["POST"])
def clear_comment():
    comment = request.form["clear_text"]
    clear_db = Admin(clear_word=comment)
    db.session.add(clear_db)
    db.session.commit()
    flash("お疲れ様コメントを保存しました")
    return redirect(url_for("admin"))
