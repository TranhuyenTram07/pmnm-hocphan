from flask import Flask, request, redirect, url_for, abort, make_response, jsonify
from html import escape
import math


app = Flask(__name__)

app.json.ensure_ascii = False


STUDENTS = {
    "23T1020001": {
        "name": "Nguyễn Văn An",
        "lop": "K47A",
        "scores": {
            "PMMNM": 8.5,
            "CSDL": 7.0,
            "MMT": 9.0
        }
    },
    "23T1020002": {
        "name": "Trần Thị Bình",
        "lop": "K47A",
        "scores": {
            "PMMNM": 6.0,
            "CSDL": 5.5,
            "MMT": 7.0
        }
    },
    "23T1020003": {
        "name": "Lê Hoàng Cường",
        "lop": "K47B",
        "scores": {
            "PMMNM": 9.5,
            "CSDL": 9.0
        }
    },
    "23T1020004": {
        "name": "Phạm Minh Dũng",
        "lop": "K47B",
        "scores": {
            "PMMNM": 4.0,
            "CSDL": 3.5,
            "MMT": 5.0
        }
    },
    "23T1020005": {
        "name": "Hoàng Thu Hà",
        "lop": "K47A",
        "scores": {}
    },
    "23T1020006": {
        "name": "Võ Quốc Khánh",
        "lop": "K47C",
        "scores": {
            "PMMNM": 7.5,
            "MMT": 8.0
        }
    }
}


# =========================
# PHẦN 0 - HÀM PHỤ
# =========================

def average(scores):
    if not scores:
        return None

    avg = sum(scores.values()) / len(scores)
    return round(avg, 2)


def rank(avg):
    if avg is None:
        return "Chưa có điểm"
    if avg >= 8.5:
        return "Giỏi"
    if avg >= 7.0:
        return "Khá"
    if avg >= 5.0:
        return "Trung bình"
    return "Yếu"


def student_summary(mssv):
    student = STUDENTS[mssv]
    avg = average(student["scores"])

    return {
        "mssv": mssv,
        "name": student["name"],
        "lop": student["lop"],
        "scores": dict(student["scores"]),
        "average": avg,
        "rank": rank(avg)
    }


def layout(title, body):
    safe_title = escape(str(title))

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>{safe_title} - Sổ điểm</title>
</head>
<body>
    <nav>
        <a href="{url_for('home')}">Trang chủ</a> |
        <a href="{url_for('student_list')}">Sinh viên</a> |
        <a href="{url_for('search')}">Tìm kiếm</a>
    </nav>

    <hr>

    {body}
</body>
</html>"""


# =========================
# CÂU 1 - TRANG CHỦ
# =========================

@app.route("/")
def home():
    total = len(STUDENTS)
    classes = len(set(student["lop"] for student in STUDENTS.values()))

    body = f"""
    <h1>Sổ điểm</h1>

    <p>Tổng số sinh viên: {escape(str(total))}</p>
    <p>Số lớp: {escape(str(classes))}</p>

    <p>
        <a href="{url_for('student_list')}">Xem danh sách sinh viên</a>
    </p>

    <p>
        <a href="{url_for('api_students')}">Xem API sinh viên</a>
    </p>
    """

    return layout("Trang chủ", body)


# =========================
# CÂU 2 - DANH SÁCH
# =========================

@app.route("/students")
def student_list():
    lop = request.args.get("lop")

    classes = sorted(set(student["lop"] for student in STUDENTS.values()))

    students = []

    for mssv, student in STUDENTS.items():
        if lop and student["lop"].lower() != lop.lower():
            continue

        students.append(student_summary(mssv))

    filter_links = [
        f'<a href="{url_for("student_list")}">Tất cả</a>'
    ]

    for class_name in classes:
        filter_links.append(
            f'<a href="{url_for("student_list", lop=class_name)}">'
            f'{escape(class_name)}</a>'
        )

    body = """
    <h1>Danh sách sinh viên</h1>

    <p>
        Thanh lọc:
        """ + " | ".join(filter_links) + """
    </p>
    """

    if not students:
        body += "<p>Không có sinh viên phù hợp.</p>"
    else:
        body += """
        <table border="1" cellpadding="8">
            <tr>
                <th>MSSV</th>
                <th>Họ tên</th>
                <th>Lớp</th>
                <th>Điểm TB</th>
                <th>Xếp loại</th>
            </tr>
        """

        for student in students:
            avg = (
                "—"
                if student["average"] is None
                else escape(str(student["average"]))
            )

            body += f"""
            <tr>
                <td>
                    <a href="{url_for(
                        'student_detail',
                        mssv=student['mssv']
                    )}">
                        {escape(student["mssv"])}
                    </a>
                </td>

                <td>{escape(student["name"])}</td>
                <td>{escape(student["lop"])}</td>
                <td>{avg}</td>
                <td>{escape(student["rank"])}</td>
            </tr>
            """

        body += "</table>"

    return layout("Sinh viên", body)


# =========================
# CÂU 3 - CHI TIẾT
# =========================

@app.route("/students/<mssv>")
def student_detail(mssv):
    if mssv not in STUDENTS:
        abort(
            404,
            description=f"Không có sinh viên với MSSV = {mssv}."
        )

    student = student_summary(mssv)

    avg = (
        "—"
        if student["average"] is None
        else escape(str(student["average"]))
    )

    body = f"""
    <h1>Chi tiết sinh viên</h1>

    <p>
        <strong>Họ tên:</strong>
        {escape(student["name"])}
    </p>

    <p>
        <strong>MSSV:</strong>
        {escape(student["mssv"])}
    </p>

    <p>
        <strong>Lớp:</strong>
        <a href="{url_for(
            'student_list',
            lop=student['lop']
        )}">
            {escape(student["lop"])}
        </a>
    </p>

    <p>
        <strong>Điểm TB:</strong>
        {avg}
    </p>

    <p>
        <strong>Xếp loại:</strong>
        {escape(student["rank"])}
    </p>

    <h2>Bảng điểm</h2>
    """

    if student["scores"]:
        body += """
        <table border="1" cellpadding="8">
            <tr>
                <th>Học phần</th>
                <th>Điểm</th>
            </tr>
        """

        for course, score in student["scores"].items():
            body += f"""
            <tr>
                <td>{escape(course)}</td>
                <td>{escape(str(score))}</td>
            </tr>
            """

        body += "</table>"
    else:
        body += "<p>Chưa có điểm.</p>"

    body += f"""
    <p>
        <a href="{url_for(
            'export_score',
            mssv=student['mssv']
        )}">
            Tải bảng điểm (CSV)
        </a>
    </p>

    <p>
        Link rút gọn:
        <a href="{url_for('short_student', mssv=student['mssv'])}">
            {url_for('short_student', mssv=student['mssv'])}
        </a>
    </p>
    """

    return layout("Chi tiết sinh viên", body)


# =========================
# CÂU 4 - LINK RÚT GỌN
# =========================

@app.route("/sv/<mssv>")
def short_student(mssv):
    return redirect(
        url_for("student_detail", mssv=mssv),
        code=301
    )


# =========================
# CÂU 5 - CSV
# =========================

@app.route("/students/<mssv>/export")
def export_score(mssv):
    if mssv not in STUDENTS:
        abort(
            404,
            description=f"Không có sinh viên với MSSV = {mssv}."
        )

    student = STUDENTS[mssv]

    lines = ["hoc_phan,diem"]

    for course, score in student["scores"].items():
        lines.append(
            f"{course},{score}"
        )

    csv_data = "\n".join(lines)

    response = make_response(csv_data)

    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = (
        f"attachment; filename=diem_{mssv}.csv"
    )

    return response


# =========================
# CÂU 6 - TÌM KIẾM
# =========================

@app.route("/search")
def search():
    q = request.args.get("q", "")

    q_lower = q.lower()

    results = []

    if q:
        for mssv, student in STUDENTS.items():
            if (
                q_lower in student["name"].lower()
                or q_lower in mssv.lower()
            ):
                results.append(student_summary(mssv))

    body = f"""
    <h1>Tìm kiếm sinh viên</h1>

    <form method="get" action="{url_for('search')}">
        <input
            type="text"
            name="q"
            value="{escape(q)}"
        >

        <button type="submit">
            Tìm kiếm
        </button>
    </form>
    """

    if q:
        body += f"""
        <p>
            Tìm thấy {escape(str(len(results)))} kết quả cho
            “{escape(q)}”
        </p>
        """

        if results:
            body += "<ul>"

            for student in results:
                body += f"""
                <li>
                    <a href="{url_for(
                        'student_detail',
                        mssv=student['mssv']
                    )}">
                        {escape(student["name"])}
                        - {escape(student["mssv"])}
                    </a>
                </li>
                """

            body += "</ul>"
        else:
            body += "<p>Không có sinh viên phù hợp.</p>"

    return layout("Tìm kiếm", body)


# =========================
# CÂU 7 - API ĐỌC
# =========================

@app.route("/api/students")
def api_students():
    lop = request.args.get("lop")

    min_avg_raw = request.args.get("min_avg")

    if min_avg_raw is None:
        min_avg = None
    else:
        try:
            min_avg = float(min_avg_raw)

            if not math.isfinite(min_avg):
                raise ValueError

        except ValueError:
            abort(
                400,
                description="min_avg phải là một số hợp lệ."
            )

    results = []

    for mssv, student in STUDENTS.items():
        if lop and student["lop"].lower() != lop.lower():
            continue

        summary = student_summary(mssv)

        if min_avg is not None:
            if summary["average"] is None:
                continue

            if summary["average"] < min_avg:
                continue

        results.append(summary)

    return jsonify(results)


@app.route("/api/students/<mssv>")
def api_student_detail(mssv):
    if mssv not in STUDENTS:
        abort(
            404,
            description=f"Không có sinh viên với MSSV = {mssv}."
        )

    return jsonify(student_summary(mssv))


# =========================
# CÂU 8 - API QUẢN LÝ ĐIỂM
# =========================

@app.route(
    "/api/students/<mssv>/scores/<course>",
    methods=["GET", "PUT", "DELETE"]
)
def api_score(mssv, course):
    if mssv not in STUDENTS:
        abort(
            404,
            description=f"Không có sinh viên với MSSV = {mssv}."
        )

    course = course.upper()
    scores = STUDENTS[mssv]["scores"]

    if request.method == "GET":
        if course not in scores:
            abort(
                404,
                description=(
                    f"Không có điểm học phần {course} "
                    f"cho sinh viên {mssv}."
                )
            )

        return jsonify({
            "mssv": mssv,
            "course": course,
            "score": scores[course]
        })

    if request.method == "PUT":
        score_raw = request.args.get("score")

        if score_raw is None:
            abort(
                400,
                description="Thiếu tham số score."
            )

        try:
            score = float(score_raw)

            if not math.isfinite(score):
                raise ValueError

        except ValueError:
            abort(
                400,
                description="score phải là một số hợp lệ."
            )

        if score < 0 or score > 10:
            abort(
                400,
                description="score phải nằm trong khoảng từ 0 đến 10."
            )

        is_new = course not in scores

        scores[course] = score

        result = {
            "mssv": mssv,
            "course": course,
            "score": score,
            "average": average(scores)
        }

        if is_new:
            response = make_response(
                jsonify(result),
                201
            )
        else:
            response = make_response(
                jsonify(result),
                200
            )

        response.headers["Location"] = url_for(
            "api_score",
            mssv=mssv,
            course=course
        )

        return response

    if request.method == "DELETE":
        if course not in scores:
            abort(
                404,
                description=(
                    f"Không có điểm học phần {course} "
                    f"cho sinh viên {mssv}."
                )
            )

        del scores[course]

        return make_response("", 204)


# =========================
# CÂU 9 - XỬ LÝ LỖI
# =========================

@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(405)
def handle_error(error):
    if error.code == 400:
        title = "Dữ liệu không hợp lệ"
    elif error.code == 404:
        title = "Không tìm thấy"
    else:
        title = "Phương thức không được hỗ trợ"

    description = error.description or title

    if request.path.startswith("/api/"):
        return jsonify({
            "error": title,
            "detail": description
        }), error.code

    body = f"""
    <h1>{escape(str(error.code))} - {escape(title)}</h1>

    <p>{escape(str(description))}</p>

    <p>
        <a href="{url_for('home')}">Về trang chủ</a>
    </p>

    <p>
        <a href="{url_for('student_list')}">
            Danh sách sinh viên
        </a>
    </p>

    <p>
        <a href="{url_for('search')}">
            Tìm kiếm
        </a>
    </p>
    """

    return layout(title, body), error.code


if __name__ == "__main__":
    app.run(debug=True, port=8000)