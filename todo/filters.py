from datetime import date, datetime


# 自定义的 fmt_datetime 过滤器
def fmt_datetime(value, format_='%Y-%m-%d'):
    if isinstance(value, (date, datetime)):
        return value.strftime(format_)
    return value


def init_app(app):
    # 注册自定义过滤器
    app.jinja_env.filters['fmt_datetime'] = fmt_datetime
