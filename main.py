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
                   "AND t1.document_end = (select max(document_end) from netdb_dstobj) "
                   "AND t2.link = -3 "
                   "ORDER BY t1.link desc",
                   (oid, ))
    # cursor.execute("SELECT link, dst "
    #                "FROM netdb_dstobj "
    #                "WHERE src = '%s' "
    #                "AND document_end = (select max(document_end) from netdb_dstobj)"
    #                "ORDER BY src desc, link desc",
    #                (oid,))
    objects = cursor.fetchall()
    cursor.execute("SELECT dst "
                   "FROM netdb_dststring "
                   "WHERE src = '%s' "
                   "AND document_end = (select max(document_end) from netdb_dststring) "
                   "ORDER BY src desc, link desc",
                   (oid, ))
    strings = cursor.fetchall()
    return jsonify({
        'objects': list(
            {'link': o[0], 'oid': o[1], 'str': o[2]} for o in objects
        ),
        'strings': list(s[0] for s in strings)
    })


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


@app.route("/")
def index():
    return send_html("index.html")


@app.route("/style.css")
def style():
    return send_css("style.css")


def main():
    port = 7002
    host = "0.0.0.0"
    from waitress import serve
    serve(app, host=host, port=port)


if __name__ == '__main__':
    main()
