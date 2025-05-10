from datetime import datetime, timedelta

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from todo.auth import login_required
from todo.db import get_db

bp = Blueprint('todo', __name__)


@bp.route('/')
@login_required
def index():
    db = get_db()
    todo_today = db.execute(
        'SELECT t.id, t.content, t.finished FROM todo t'
        ' JOIN user u ON t.user_id = u.id'
        ' WHERE u.id = ? AND DATE(t.schedule) = ?'
        ' ORDER BY t.created DESC',
        (g.user['id'], datetime.now().date())
    ).fetchall()

    return render_template('todo/index.html', todo_today=todo_today)


@bp.route('/list')
@login_required
def list_():
    td = datetime.today().date()
    # 仅显示今天以后（不含今天）的未完成待办事项
    todo_list = get_db().execute(
        "SELECT * FROM todo WHERE user_id = ?"
        " AND finished = 0"
        " AND(schedule is NULL OR DATE(schedule) > ?)",
        (g.user['id'], td)
    ).fetchall()
    return render_template("/todo/list.html", todo_list=todo_list)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        content = request.form['content']
        finished = request.form['finished']
        # 未指定日期（传递空字符串）时，数据库存NULL
        schedule = request.form['schedule'] or None
        from_ = request.args.get('from')
        errors = list()

        print(schedule, type(schedule))

        if not content:
            errors.append('请输入待办事项')
        elif len(content) > 32:
            errors.append('待办事项最多输入32个字符')

        if schedule:
            try:
                schedule = datetime.strptime(schedule, '%Y-%m-%d')
            except ValueError:
                errors.append('日期格式有误')

        if not errors:
            db = get_db()
            db.execute(
                'INSERT INTO todo (content, finished, schedule, user_id) VALUES (?, ?, ?, ?)',
                (content, finished, schedule, g.user['id'])
            )
            db.commit()

            if from_ == 'list':
                return redirect(url_for('todo.list_'))
            return redirect(url_for('index'))

        flash(errors[0])

    return render_template('todo/create.html')


def get_todo(id_):
    """获取指定ID的待办事项"""
    todo = get_db().execute(
        'SELECT * FROM todo WHERE id = ?', (id_,)
    ).fetchone()

    if todo is None:
        abort(404, f'id为{id_}的待办不存在')

    if todo['user_id'] != g.user['id']:
        abort(403)

    return todo


@bp.route('/update/<int:id_>', methods=('GET', 'POST'))
@login_required
def update(id_):
    todo = get_todo(id_)

    if request.method == 'POST':
        content = request.form['content']
        finished = request.form['finished']
        schedule = request.form['schedule'] or None
        from_ = request.args.get('from')
        errors = list()

        if not content:
            errors.append('请输入待办事项')
        elif len(content) > 32:
            errors.append('待办事项最多输入32个字符')

        if schedule:
            try:
                schedule = datetime.strptime(schedule, '%Y-%m-%d')
            except ValueError:
                errors.append('日期格式有误')

        if not errors:
            db = get_db()
            db.execute(
                'UPDATE todo SET content = ?, finished = ?, schedule = ? WHERE id = ?',
                (content, finished, schedule, id_)
            )
            db.commit()

            if from_ == 'list':
                return redirect(url_for('todo.list_'))
            return redirect(url_for('index'))

        flash(errors[0])
    return render_template('todo/update.html', todo=todo)


@bp.route('/delete/<int:id_>', methods=('POST',))
@login_required
def delete(id_):
    todo = get_todo(id_)
    from_ = request.args.get('from')
    db = get_db()
    db.execute(
        'DELETE FROM todo WHERE id = ?', (id_,)
    )
    db.commit()

    if from_ == 'list':
        return redirect(url_for('todo.list_'))
    return redirect(url_for('index'))
