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
        ' WHERE u.id = ? AND DATE(t.created) = ?'
        ' ORDER BY t.created DESC',
        (g.user['id'], datetime.now().date())
    ).fetchall()

    yesterday = datetime.now().date() - timedelta(days=1)
    todo_yesterday = db.execute(
        'SELECT t.id, t.content, t.finished FROM todo t'
        ' JOIN user u ON t.user_id = u.id'
        ' WHERE u.id = ? AND DATE(t.created) = ?'
        ' ORDER BY t.created DESC',
        (g.user['id'], yesterday)
    ).fetchall()

    return render_template(
        'todo/index.html', todo_today=todo_today, todo_yesterday=todo_yesterday
    )


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        content = request.form['content']
        finished = request.form['finished']
        error = None

        if not content:
            error = '请输入待办事项'
        elif len(content) > 32:
            error = '待办事项最多输入32个字符'

        if error is None:
            db = get_db()
            db.execute(
                'INSERT INTO todo (content, finished, user_id) VALUES (?, ?, ?)',
                (content, finished, g.user['id'])
            )
            db.commit()
            return redirect(url_for('index'))

        flash(error)

    return render_template('todo/create.html')


def get_todo(id):
    """获取指定ID的待办事项"""
    todo = get_db().execute(
        'SELECT * FROM todo WHERE id = ?', (id,)
    ).fetchone()

    if todo is None:
        abort(404, f'id为{id}的待办不存在')

    if todo['user_id'] != g.user['id']:
        abort(403)

    return todo


@bp.route('/update/<int:id>', methods=('GET', 'POST'))
@login_required
def update(id):
    todo = get_todo(id)

    if request.method == 'POST':
        content = request.form['content']
        finished = request.form['finished']
        error = None

        if not content:
            error = '请输入待办事项'
        elif len(content) > 32:
            error = '待办事项最多输入32个字符'

        if error is None:
            db = get_db()
            db.execute(
                'UPDATE todo SET content = ?, finished = ? WHERE id = ?',
                (content, finished, id)
            )
            db.commit()
            return redirect(url_for('index'))

        flash(error)
    return render_template('todo/update.html', todo=todo)


@bp.route('/delete/<int:id>', methods=('POST',))
@login_required
def delete(id):
    todo = get_todo(id)
    db = get_db()
    db.execute(
        'DELETE FROM todo WHERE id = ?', (id,)
    )
    db.commit()
    return redirect(url_for('index'))


@bp.route('/add/<int:id>', methods=('POST',))
@login_required
def add(id):
    todo = get_todo(id)
    db = get_db()
    db.execute(
        'INSERT INTO todo (content, finished, user_id) VALUES (?, ?, ?)',
        (todo['content'], todo['finished'], g.user['id'])
    )
    db.commit()
    return redirect(url_for('index'))
