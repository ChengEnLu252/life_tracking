from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 設定資料庫
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 定義資料模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)  # 密碼作為普通屬性

class HealthData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    blood_pressure = db.Column(db.String(20))
    heart_rate = db.Column(db.String(20))
    weight = db.Column(db.Float)

class DietData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    meal_type = db.Column(db.String(20))  # 早餐/午餐/晚餐
    calories = db.Column(db.Integer)
    notes = db.Column(db.String(100))

class SleepData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sleep_hours = db.Column(db.Float)
    sleep_quality = db.Column(db.String(20))  # 好/中/差

# 初始化資料庫
with app.app_context():
    db.create_all()

# 首頁（登入頁面）
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 驗證使用者名稱和密碼
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            return redirect(url_for('dashboard', user_id=user.id))  # 登入成功，傳遞 user_id
        else:
            return "Login failed. Please check your username and password."
    return render_template('home.html')

# 註冊頁面
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 新增使用者
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('home'))  # 註冊成功後回到登入頁面
    return render_template('register.html')

# 功能頁面
@app.route('/dashboard/<int:user_id>')
def dashboard(user_id):
    return render_template('dashboard.html', user_id=user_id)

# 新增健康資料
@app.route('/add_health/<int:user_id>', methods=['GET', 'POST'])
def add_health(user_id):
    if request.method == 'POST':
        blood_pressure = request.form['blood_pressure']
        heart_rate = request.form['heart_rate']
        weight = request.form['weight']

        new_health = HealthData(user_id=user_id, blood_pressure=blood_pressure, heart_rate=heart_rate, weight=weight)
        db.session.add(new_health)
        db.session.commit()
        return redirect(url_for('dashboard', user_id=user_id))
    return render_template('add_health.html')

# 新增飲食資料
@app.route('/add_diet/<int:user_id>', methods=['GET', 'POST'])
def add_diet(user_id):
    if request.method == 'POST':
        meal_type = request.form['meal_type']
        calories = request.form['calories']
        notes = request.form['notes']

        new_diet = DietData(user_id=user_id, meal_type=meal_type, calories=calories, notes=notes)
        db.session.add(new_diet)
        db.session.commit()
        return redirect(url_for('dashboard', user_id=user_id))
    return render_template('add_diet.html')

# 新增睡眠資料
@app.route('/add_sleep/<int:user_id>', methods=['GET', 'POST'])
def add_sleep(user_id):
    if request.method == 'POST':
        sleep_hours = request.form['sleep_hours']
        sleep_quality = request.form['sleep_quality']

        new_sleep = SleepData(user_id=user_id, sleep_hours=sleep_hours, sleep_quality=sleep_quality)
        db.session.add(new_sleep)
        db.session.commit()
        return redirect(url_for('dashboard', user_id=user_id))
    return render_template('add_sleep.html')

#########################
# 查看健康資料
@app.route('/view_health/<int:user_id>')
def view_health(user_id):
    health_data = HealthData.query.filter_by(user_id=user_id).all()
    return render_template('view_health.html', health_data=health_data, user_id=user_id)

# 編輯健康資料
@app.route('/edit_health/<int:health_id>', methods=['GET', 'POST'])
def edit_health(health_id):
    health = HealthData.query.get_or_404(health_id)
    if request.method == 'POST':
        health.blood_pressure = request.form['blood_pressure']
        health.heart_rate = request.form['heart_rate']
        health.weight = request.form['weight']
        db.session.commit()
        return redirect(url_for('view_health', user_id=health.user_id))
    return render_template('edit_health.html', health=health)

# 刪除健康資料
@app.route('/delete_health/<int:health_id>')
def delete_health(health_id):
    health = HealthData.query.get_or_404(health_id)
    user_id = health.user_id
    db.session.delete(health)
    db.session.commit()
    return redirect(url_for('view_health', user_id=user_id))

if __name__ == '__main__':
    app.run(debug=True)
