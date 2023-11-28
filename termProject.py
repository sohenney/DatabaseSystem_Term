import pyodbc

# ODBC 연결 문자열 생성
conn_str = (
    r'DRIVER={MySQL ODBC 8.2 Unicode Driver};'
    r'SERVER=192.168.17.3;'
    r'DATABASE=MyDiary;'
    r'USER=shlee;'
    r'PASSWORD=ththgus0642;'
    r'charset=utf8;'
)

# 데이터베이스 연결
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Flask 라우트 정의
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/diaries', methods=['GET', 'POST'])
def diaries():
    if request.method == 'POST':
        # 사용자 입력을 받아 데이터베이스에 삽입 또는 검색 등의 작업 수행
        # 예: title = request.form['title']
        #     content = request.form['content']
        #     cursor.execute("INSERT INTO Diary (title, content) VALUES (?, ?)", (title, content))
        #     conn.commit()
        pass

    # 데이터베이스에서 일기 목록을 가져와서 템플릿에 전달
    cursor.execute("SELECT * FROM Diary")
    diaries = cursor.fetchall()

    return render_template('diaries.html', diaries=diaries)

# 실행
if __name__ == '__main__':
    app.run(debug=True)