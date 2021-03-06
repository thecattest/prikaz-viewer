from flask import Flask, request, make_response, jsonify, Response
import os
import psycopg2


app = Flask(__name__)
conn = psycopg2.connect(user="prikaz",
                        password="prikazpassword",
                        host="127.0.0.1",
                        port="5432",
                        database="prikaz")
cursor = conn.cursor()


@app.route("/api/", methods=["POST"])
def api():
    oid = int(request.get_json()["oid"])
    cursor.execute("SELECT t1.link, t1.dst, t2.dst "
                   "FROM netdb_dstobj t1 "
                   "LEFT JOIN netdb_dststring t2 on t1.link = t2.src "
                   "WHERE t1.src = '%s' "
                   "AND t1.document_end = '9999-12-31 23:59:59.999999+03' "
                   "AND t2.document_end = '9999-12-31 23:59:59.999999+03' "
                   "AND t2.link = -3 "
                   "ORDER BY t1.link desc",
                   (oid, ))
    objects = cursor.fetchall()
    return jsonify({
        'obj': list(
            {'link': o[0], 'oid': o[1], 'str': o[2]} for o in objects
        ),
        'string': get_dsts('netdb_dststring', oid),
        'file': get_dsts('netdb_dstfile', oid),
        'integer': get_dsts('netdb_dstint', oid),
        'float': get_dsts('netdb_dstfloat', oid),
        'boolean': get_dsts('netdb_dstbool', oid),
        'datetime': get_dsts('netdb_dstdatetime', oid),
    })


def get_dsts(tablename, oid):
    cursor.execute("SELECT t1.link, t1.dst, t2.dst "
                   "FROM {} t1 "
                   "LEFT JOIN netdb_dststring t2 on t1.link = t2.src "
                   "WHERE t1.src = '%s' "
                   "AND t1.document_end = '9999-12-31 23:59:59.999999+03' "
                   "AND t2.document_end = '9999-12-31 23:59:59.999999+03' "
                   "AND t2.link = -3 "
                   "ORDER BY t1.link desc".format(tablename, tablename),
                   (oid,))
    dsts = cursor.fetchall()
    return list({'link': d[0], 'value': d[1], 'str': d[2]} for d in dsts)


def root_dir():
    return os.path.abspath(os.path.dirname(__file__))


def get_file(filename):
    try:
        src = os.path.join(root_dir(), filename)
        return open(src)
    except IOError as exc:
        return str(exc)


def send_html(name):
    content = get_file(name).read()
    return Response(content, mimetype="text/html")


def send_css(name):
    content = get_file(name).read()
    return Response(content, mimetype="text/css")


def send_js(name):
    content = get_file(name).read()
    return Response(content, mimetype="text/js")


@app.route("/")
def index():
    return send_html("index.html")


@app.route("/style.css")
def style():
    return send_css("style.css")


@app.route("/axios.js")
def axios():
    return send_js("axios.js")


@app.route("/vue.js")
def vue():
    return send_js("vue.js")


def main():
    port = 7002
    host = "0.0.0.0"
    from waitress import serve
    serve(app, host=host, port=port)


if __name__ == '__main__':
    main()
