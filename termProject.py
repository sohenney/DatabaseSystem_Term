import pyodbc

# 회원관리
def user_exists(username):
    cursor.execute("SELECT COUNT(*) FROM User WHERE Username = ?", username)
    return cursor.fetchone()[0] > 0

def register_user():
    print("회원가입을 시작합니다.")
    username = input("사용할 계정명을 입력하세요: ")
    
    if user_exists(username):
        print("이미 존재하는 계정입니다. 로그인하세요.")
        return

    password = input("비밀번호를 입력하세요: ")

    # 회원가입 정보를 User 테이블에 추가
    cursor.execute("INSERT INTO User (Username, Password) VALUES (?, ?)", username, password)
    conn.commit()

    print("회원가입이 완료되었습니다. 로그인하세요.")

def login_user():
    print("로그인을 시작합니다.")
    username = input("계정명을 입력하세요: ")

    if not user_exists(username):
        print("존재하지 않는 계정입니다. 회원가입하세요.")
        return

    password = input("비밀번호를 입력하세요: ")

    # 입력한 계정과 비밀번호가 일치하는지 확인
    cursor.execute("SELECT * FROM User WHERE Username = ? AND Password = ?", username, password)
    user = cursor.fetchone()

    if user:
        print("로그인 성공! 환영합니다, {}님.".format(username))
        return user
    else:
        print("비밀번호가 일치하지 않습니다.")

def delete_user(username, password):
    # 입력받은 사용자명과 비밀번호가 일치하는지 확인
    cursor.execute("SELECT * FROM User WHERE Username = ? AND Password = ?", username, password)
    user = cursor.fetchone()

    if user:
        # 사용자 정보 삭제
        cursor.execute("DELETE FROM User WHERE UserID = ?", user.UserID)
        conn.commit()
        print("회원탈퇴가 완료되었습니다.")
        return True
    else:
        print("사용자 정보가 일치하지 않습니다.")
        return False

# 다이어리 관리
def insert_diary(user_id, category_name, date, weather, mood, content, title):
    # 카테고리 ID 가져오기
    cursor.execute("SELECT CategoryID FROM Category WHERE CategoryName = ?", category_name)
    category_row = cursor.fetchone()

    if category_row:
        category_id = category_row[0]

        # Diary 테이블에 다이어리 추가
        cursor.execute("""
            INSERT INTO Diary (UserID, CategoryID, Date, Weather, Mood, Content, Title)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, user_id, category_id, date, weather, mood, content, title)
        
        conn.commit()

        print("다이어리가 성공적으로 추가되었습니다.")
    else:
        print(f"카테고리 '{category_name}'가 존재하지 않습니다.")


def fetch_user_diaries(user_id):
    # 사용자의 다이어리 조회
    cursor.execute("""
        SELECT DiaryID, Title, Date, Weather, Mood, Content
        FROM Diary
        WHERE UserID = ?
    """, user_id)
    
    return cursor.fetchall()

def fetch_diary_by_id(diary_id):
    # 특정 ID의 다이어리 조회
    cursor.execute("""
        SELECT Title, Date, Weather, Mood, Content
        FROM Diary
        WHERE DiaryID = ?
    """, diary_id)

    return cursor.fetchone()

def update_diary(diary_id, new_title, new_content):
    # 다이어리 업데이트
    cursor.execute("""
        UPDATE Diary
        SET Title = ?, Content = ?
        WHERE DiaryID = ?
    """, new_title, new_content, diary_id)
    
    conn.commit()

def delete_diary_by_id(diary_id):
    # 다이어리 삭제
    cursor.execute("DELETE FROM Diary WHERE DiaryID = ?", diary_id)
    
    conn.commit()

def create_diary(logged_in_user):
    # Display a list of available categories
    cursor.execute("SELECT CategoryName FROM Category")
    categories = [row.CategoryName for row in cursor.fetchall()]
    
    if not categories:
        print("카테고리가 존재하지 않습니다. 먼저 카테고리를 추가하세요.")
        return

    print("다이어리의 카테고리를 선택하세요:")
    for i, category in enumerate(categories, start=1):
        print(f"{i}. {category}")

    # Get user's category choice
    category_choice = input("선택하세요 (숫자): ")

    try:
        category_index = int(category_choice) - 1
        selected_category = categories[category_index]
    except (ValueError, IndexError):
        print("올바른 선택이 아닙니다. 다이어리 작성을 취소합니다.")
        return

    date = input("날짜를 입력하세요: ")
    weather = input("날씨를 입력하세요: ")
    mood = input("기분을 입력하세요: ")
    content = input("내용을 입력하세요: ")
    title = input("다이어리의 제목을 입력하세요: ")

    insert_diary(logged_in_user.UserID, selected_category, date, weather, mood, content, title)
    
def view_diaries(logged_in_user):
    user_diaries = fetch_user_diaries(logged_in_user.UserID)
    print("\n사용자의 다이어리 목록:")
    for diary in user_diaries:
        print(f"다이어리 ID: {diary.DiaryID}, 제목: {diary.Title}, 날짜: {diary.Date}")

def edit_diary(logged_in_user):
    diary_id = input("수정할 다이어리의 ID를 입력하세요: ")
    diary = fetch_diary_by_id(diary_id)

    if diary:
        print("\n다이어리 정보:")
        print(f"제목: {diary.Title}, 날짜: {diary.Date}, 날씨: {diary.Weather}, 기분: {diary.Mood}")
        print("내용:", diary.Content)

        new_title = input("\n새로운 제목을 입력하세요 (변경하지 않을 경우 엔터): ")
        new_content = input("새로운 내용을 입력하세요 (변경하지 않을 경우 엔터): ")

        update_diary(diary_id, new_title, new_content)
        print("다이어리가 성공적으로 수정되었습니다.")
    else:
        print("해당 ID의 다이어리가 존재하지 않습니다.")

def delete_diary(logged_in_user):
    diary_id = input("삭제할 다이어리의 ID를 입력하세요: ")
    diary = fetch_diary_by_id(diary_id)

    if diary:
        print("\n다이어리 정보:")
        print(f"제목: {diary.Title}, 날짜: {diary.Date}, 날씨: {diary.Weather}, 기분: {diary.Mood}")
        print("내용:", diary.Content)

        confirmation = input("\n정말로 삭제하시겠습니까? (y/n): ")
        if confirmation.lower() == "y":
            delete_diary_by_id(diary_id)
            print("다이어리가 성공적으로 삭제되었습니다.")
        else:
            print("다이어리 삭제가 취소되었습니다.")
    else:
        print("해당 ID의 다이어리가 존재하지 않습니다.")

# PyODBC 연결 문자열 생성
conn_str = (
    r'DRIVER={MySQL ODBC 8.2 Unicode Driver};'
    r'SERVER=192.168.17.3;'
    r'DATABASE=MyDiary;'
    r'USER=shlee;'
    r'PASSWORD=ththgus0642;'
    r'charset=utf8;'
)

# 커넥션 생성
conn = pyodbc.connect(conn_str)

# 커서 생성
cursor = conn.cursor()

# 사용자에게 회원가입, 로그인, 탈퇴 선택
while True:
    print("""
    MyDiary 프로그램에 접속하신 걸 환영합니다!
    ** 해당 프로그램은 회원가입 후에 이용 가능합니다. **
    """)
    print("1. 회원가입\n2. 로그인\n3. 회원탈퇴\n4. 종료")
    choice = input("선택하세요: ")

    if choice == "1":
        register_user()
    elif choice == "2":
        logged_in_user = login_user()
        if logged_in_user:
            while True:
                print("""
                다이어리 및 카테고리 관리 화면입니다.
                *********************************************
                카테고리가 존재해야 다이어리 작성이 가능합니다.
                기본 카테고리는 일기가 있으며, 5을 입력해 추가 가능합니다. 
                *********************************************
                1. 다이어리 작성
                2. 다이어리 조회
                3. 다이어리 수정
                4. 다이어리 삭제
                5. 카테고리 추가
                6. 카테고리 선택
                7. 카테고리 삭제
                6. 로그아웃
                """)
                diary_choice = input("원하는 작업을 선택하세요: ")
                if diary_choice == "1":
                    create_diary(logged_in_user)
                    pass
                elif diary_choice == "2":
                    view_diaries(logged_in_user)
                    pass
                elif diary_choice == "3":
                    edit_diary(logged_in_user)
                    pass
                elif diary_choice == "4":
                    delete_diary(logged_in_user)
                    pass
                elif diary_choice == "5":
                    # 카테고리 추가 기능 추가
                    pass
                elif diary_choice == "6":
                    # 카테고리 선택 기능 추가
                    pass
                elif diary_choice == "7":
                    # 카테고리 삭제 기능 추가
                    break
                elif diary_choice == "8":
                    # 로그아웃 기능 추가
                    break
                else:
                    print("올바른 선택이 아닙니다. 다시 선택하세요.")
    elif choice == "3":
        username = input("삭제할 계정명을 입력하세요: ")
        password = input("비밀번호를 입력하세요: ")
        if delete_user(username, password):
            continue
    elif choice == "4":
        break
    else:
        print("올바른 선택이 아닙니다. 다시 선택하세요.")

# 연결 종료
conn.close()
