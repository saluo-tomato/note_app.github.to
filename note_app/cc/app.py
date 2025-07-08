from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, User, Note
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///note_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key' 

db.init_app(app)

with app.app_context():
    db.create_all()

# 首页
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('note_list'))
    return render_template('index.html')

# 注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'danger')
            return redirect(url_for('register'))
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('注册成功，请登录', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# 登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('登录成功', 'success')
            return redirect(url_for('note_list'))
        flash('用户名或密码错误', 'danger')
        return redirect(url_for('login'))
    return render_template('login.html')

# 登出
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('已登出', 'info')
    return redirect(url_for('index'))

# 我的笔记列表
@app.route('/notes')
def note_list():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    notes = Note.query.filter_by(user_id=user_id).order_by(Note.id.desc()).all()
    return render_template('note_list.html', notes=notes)

# 创建笔记
@app.route('/notes/create', methods=['GET', 'POST'])
def create_note():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title'].strip()
        content = request.form['content'].strip()
        if not title:
            flash('标题不能为空', 'danger')
            return redirect(url_for('create_note'))
        new_note = Note(title=title, content=content, user_id=session['user_id'])
        db.session.add(new_note)
        db.session.commit()
        flash('笔记创建成功', 'success')
        return redirect(url_for('note_list'))
    return render_template('create_note.html')

# 编辑笔记
@app.route('/notes/<int:id>/edit', methods=['GET', 'POST'])
def edit_note(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    note = Note.query.get_or_404(id)
    if note.user_id != session['user_id']:
        flash('无权限编辑此笔记', 'danger')
        return redirect(url_for('note_list'))
    if request.method == 'POST':
        note.title = request.form['title'].strip()
        note.content = request.form['content'].strip()
        db.session.commit()
        flash('笔记更新成功', 'success')
        return redirect(url_for('note_list'))
    return render_template('edit_note.html', note=note)

if __name__ == '__main__':
    app.run(debug=True)
