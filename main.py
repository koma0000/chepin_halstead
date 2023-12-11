from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import math
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqllite.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255))
    code = db.Column(db.Text)

class HalsteadMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    total_operators = db.Column(db.Integer)
    total_operands = db.Column(db.Integer)
    unique_operators = db.Column(db.Integer)
    unique_operands = db.Column(db.Integer)
    program_length = db.Column(db.Integer)
    vocabulary = db.Column(db.Integer)
    program_volume = db.Column(db.Float)
    program_difficulty = db.Column(db.Float)
    program_effort = db.Column(db.Float)
    programming_time = db.Column(db.Float)
    programming_errors = db.Column(db.Float)


class ChepinMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    P = db.Column(db.Float)
    M = db.Column(db.Float)
    C = db.Column(db.Float)
    T = db.Column(db.Float)
    Q = db.Column(db.Float)

@app.route('/calculate_halstead', methods=['POST'])
def calculate_halstead():
    data = request.json
    description = data.get('description')
    code = data.get('code')

    program = Program(description=description, code=code)
    db.session.add(program)
    db.session.commit()

    halstead_metrics = HalsteadMetrics(
        program_id=program.id,
        total_operators=0,
        total_operands=0,
        unique_operators=0,
        unique_operands=0,
        program_length=0,
        vocabulary=0,
        program_volume=0.0,
        program_difficulty=0.0,
        program_effort=0.0,
        programming_time=0.0,
        programming_errors=0.0
    )

    operators = {'+', '-', '*', '/', '=', '==', '!=', '<', '>', '<=', '>=', 'and', 'or', 'not', 'if', 'else', 'while', 'for', 'in', 'def', 'return'}
    for token in code.split():
        if token in operators:
            halstead_metrics.total_operators += 1
        else:
            halstead_metrics.total_operands += 1

    halstead_metrics.unique_operators = len(operators)
    halstead_metrics.unique_operands = len(set(code.split()))

    halstead_metrics.program_length = halstead_metrics.total_operators + halstead_metrics.total_operands
    halstead_metrics.vocabulary = halstead_metrics.unique_operators + halstead_metrics.unique_operands
    halstead_metrics.program_volume = (halstead_metrics.total_operators + halstead_metrics.total_operands) * (math.log2(halstead_metrics.unique_operators + halstead_metrics.unique_operands))
    halstead_metrics.program_difficulty = (halstead_metrics.unique_operators / 2) * (halstead_metrics.total_operands / halstead_metrics.unique_operands)
    halstead_metrics.program_effort = (halstead_metrics.unique_operators / 2) * (halstead_metrics.total_operands / halstead_metrics.unique_operands) * (halstead_metrics.total_operators + halstead_metrics.total_operands)
    halstead_metrics.programming_time = (halstead_metrics.unique_operators / 2) * (halstead_metrics.total_operands / halstead_metrics.unique_operands) / 18
    halstead_metrics.programming_errors = (halstead_metrics.unique_operators / 2) * (halstead_metrics.total_operands / halstead_metrics.unique_operands)**2 / 3000

    db.session.add(halstead_metrics)
    db.session.commit()

    result = {
        'program_id': program.id,
        'total_operators': halstead_metrics.total_operators,
        'total_operands': halstead_metrics.total_operands,
        'unique_operators': halstead_metrics.unique_operators,
        'unique_operands': halstead_metrics.unique_operands,
        'program_length': halstead_metrics.program_length,
        'vocabulary': halstead_metrics.vocabulary,
        'program_volume': halstead_metrics.program_volume,
        'program_difficulty': halstead_metrics.program_difficulty,
        'program_effort': halstead_metrics.program_effort,
        'programming_time': halstead_metrics.programming_time,
        'programming_errors': halstead_metrics.programming_errors
    }

    return jsonify(result)



@app.route('/calculate_chepin/<int:program_id>', methods=['POST'])
def calculate_chepin(program_id):
    chepin_metrics = ChepinMetrics.query.filter_by(program_id=program_id).first()
    if chepin_metrics:
        db.session.delete(chepin_metrics)

    db.session.commit()
    data = request.json

    # Получаем необходимые данные из JSON-ввода
    P = data.get('P')
    M = data.get('M')
    C = data.get('C')
    T = data.get('T')

    # Получаем программу из базы данных
    program = Program.query.get_or_404(program_id)

    # Рассчитываем метрику Чепина с использованием заданной формулы и коэффициентов
    a1 = 1
    a2 = 2
    a3 = 3
    a4 = 0.5

    Q = a1 * P + a2 * M + a3 * C + a4 * T

    # Создаем экземпляр ChepinMetrics и сохраняем его в базу данных
    chepin_metrics = ChepinMetrics(
        program_id=program.id,
        P=P,
        M=M,
        C=C,
        T=T,
        Q=Q
    )

    db.session.add(chepin_metrics)
    db.session.commit()

    result = {
        'program_id': program.id,
        'program_code': program.code,
        'program_des': program.description,
        'P': P,
        'M': M,
        'C': C,
        'T': T,
        'Q': Q
    }

    return jsonify(result)


@app.route('/all_programs', methods=['GET'])
def all_programs():
    # Получаем все программы из базы данных
    all_programs = Program.query.all()

    # Создаем список для хранения результатов
    result_list = []

    # Итерируем по всем программам и получаем соответствующие метрики
    for program in all_programs:
        program_metrics = {
            'program_id': program.id,
            'program_code': program.code,
            'program_des': program.description,
        }

        # Получаем метрики из таблицы halstead_metrics
        halstead_metrics = HalsteadMetrics.query.filter_by(program_id=program.id).first()
        if halstead_metrics:
            program_metrics.update({
                'halstead_total_operators': halstead_metrics.total_operators,
                'halstead_total_operands': halstead_metrics.total_operands,
                'halstead_unique_operators': halstead_metrics.unique_operators,
                'halstead_unique_operands': halstead_metrics.unique_operands,
                'halstead_program_length': halstead_metrics.program_length,
                'halstead_vocabulary': halstead_metrics.vocabulary,
                'halstead_program_volume': halstead_metrics.program_volume,
                'halstead_program_difficulty': halstead_metrics.program_difficulty,
                'halstead_program_effort': halstead_metrics.program_effort,
                'halstead_programming_time': halstead_metrics.programming_time,
                'halstead_programming_errors': halstead_metrics.programming_errors,
            })

        # Получаем метрики из таблицы chepin_metrics
        chepin_metrics = ChepinMetrics.query.filter_by(program_id=program.id).first()
        if chepin_metrics:
            program_metrics.update({
                'chepin_P': chepin_metrics.P,
                'chepin_M': chepin_metrics.M,
                'chepin_C': chepin_metrics.C,
                'chepin_T': chepin_metrics.T,
                'chepin_Q': chepin_metrics.Q,
            })

        result_list.append(program_metrics)

    return jsonify(result_list)


@app.route('/delete_program/<int:program_id>', methods=['DELETE', 'OPTIONS'])
def delete_program(program_id):
    if request.method == 'OPTIONS':
        # Это запрос для предварительной проверки CORS
        return jsonify({'message': 'CORS preflight request successful'}), 200

    # Находим программу по ID
    program = Program.query.get_or_404(program_id)

    # Удаляем запись о программе
    db.session.delete(program)
    db.session.commit()

    # Удаляем связанные записи о метриках (HalsteadMetrics и ChepinMetrics)
    halstead_metrics = HalsteadMetrics.query.filter_by(program_id=program.id).first()
    if halstead_metrics:
        db.session.delete(halstead_metrics)

    chepin_metrics = ChepinMetrics.query.filter_by(program_id=program.id).first()
    if chepin_metrics:
        db.session.delete(chepin_metrics)

    db.session.commit()

    return jsonify({'message': 'Program deleted successfully'}), 200

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

