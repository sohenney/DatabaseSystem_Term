import pyodbc

# 현재 로그인한 사용자 정보를 저장할 변수
current_user = None

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
    global current_user
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
        current_user = user  # 현재 로그인한 사용자 정보 저장
        print("로그인 성공! 환영합니다, {}님.".format(username))
        return user
    else:
        print("비밀번호가 일치하지 않습니다.")

def delete_user(username, password):
    # 입력받은 사용자명과 비밀번호가 일치하는지 확인
    cursor.execute("SELECT * FROM User WHERE Username = ? AND Password = ?", username, password)
    user = cursor.fetchone()

    if user:
        # 해당 사용자에게 속한 다이어리 및 카테고리 삭제
        cursor.execute("DELETE FROM Diary WHERE UserID = ?", user.UserID)
        cursor.execute("DELETE FROM Category WHERE UserID = ?", user.UserID)

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
    cursor.execute("SELECT CategoryID FROM Category WHERE CategoryName = ? AND UserID = ?", category_name, user_id)
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
        print(f"카테고리 '{category_name}'가 존재하지 않거나 권한이 없습니다.")

def fetch_user_diaries(logged_in_user):
    # 사용자의 다이어리 조회
    cursor.execute("""
        SELECT DiaryID, Title, Date, Weather, Mood, Content
        FROM Diary
        WHERE UserID = ?
    """, logged_in_user.UserID)

    return cursor.fetchall()

def fetch_diary_by_id(logged_in_user, diary_id):
    try:
        diary_id = int(diary_id)  # 입력받은 diary_id를 정수형으로 변환
    except ValueError:
        print("다이어리 ID는 숫자여야 합니다.")
        return None

    # 특정 ID의 다이어리 조회
    cursor.execute("""
        SELECT Title, Date, Weather, Mood, Content
        FROM Diary
        WHERE DiaryID = ? AND UserID = ?
    """, diary_id, logged_in_user.UserID)

    row = cursor.fetchone()

    if row:
        # Access tuple elements using integer indices
        diary = {
            'Title': row[0],
            'Date': row[1],
            'Weather': row[2],
            'Mood': row[3],
            'Content': row[4]
        }
        return diary
    else:
        return None

def update_diary(logged_in_user, diary_id, new_title, new_content):
    user_diaries = fetch_user_diaries(logged_in_user)

    # 다이어리 업데이트
    cursor.execute("""
        UPDATE Diary
        SET Title = ?, Content = ?
        WHERE DiaryID = ? AND UserID = ?
    """, new_title, new_content, diary_id, logged_in_user.UserID)

    if not user_diaries:
        print("데이터가 없습니다.")
    
    conn.commit()

def delete_diary_by_id(logged_in_user, diary_id):
    user_diaries = fetch_user_diaries(logged_in_user)
    
    # 다이어리 삭제
    cursor.execute("""
        DELETE FROM Diary
        WHERE DiaryID = ? AND UserID = ?
    """, diary_id, logged_in_user.UserID)
    
    if not user_diaries:
        print("데이터가 없습니다.")

    conn.commit()

def create_diary(logged_in_user):
    selected_category = select_category(logged_in_user)

    if not selected_category:
        return

    date = input("오늘의 날짜는 무엇인가요? (ex. 2023.11.30): ")
    weather = input("오늘의 날씨는 어땠나요?: ")
    mood = input("오늘 기분은 어땠나요?: ")
    content = input("내용을 입력하세요: ")
    title = input("다이어리의 제목을 입력하세요: ")

    insert_diary(logged_in_user.UserID, selected_category, date, weather, mood, content, title)

def view_diaries(logged_in_user):
    user_diaries = fetch_user_diaries(logged_in_user)

    if not user_diaries:
        print("데이터가 없습니다.")
        return

    print("\n사용자의 다이어리 목록:")
    for diary in user_diaries:
        # diary는 튜플이므로, 각 요소에 숫자 인덱스로 접근
        print(f"다이어리 ID: {diary[0]}, 제목: {diary[1]}, 날짜: {diary[2]}")

    selected_diary_id = input("\n자세히 조회할 다이어리의 ID를 입력하세요 (취소하려면 엔터): ")

    if selected_diary_id:
        diary = fetch_diary_by_id(logged_in_user, selected_diary_id)
        if diary:
            print("\n다이어리 정보:")
            print(f"제목: {diary['Title']}, 날짜: {diary['Date']}, 날씨: {diary['Weather']}, 기분: {diary['Mood']}")
            print("내용:", diary['Content'])

            ok_input = input("\nOK를 입력하면 다이어리 및 카테고리 관리 화면으로 돌아갑니다: ")
            if ok_input.lower() == "ok":
                return
        else:
            print("해당 ID의 다이어리가 존재하지 않습니다.")



def edit_diary(logged_in_user):
    user_diaries = fetch_user_diaries(logged_in_user)

    if not user_diaries:
        print("데이터가 없습니다.")
        return

    print("\n사용자의 다이어리 목록:")
    for diary in user_diaries:
        print(f"다이어리 ID: {diary[0]}, 제목: {diary[1]}, 날짜: {diary[2]}")

    diary_id = input("\n수정할 다이어리의 ID를 입력하세요 (취소하려면 엔터): ")

    if not diary_id:
        return

    # 입력받은 diary_id가 숫자인지 확인
    if not diary_id.isdigit():
        print("다이어리 ID는 숫자여야 합니다.")
        return

    # fetch_diary_by_id 함수 호출 시 logged_in_user와 diary_id를 전달
    diary = fetch_diary_by_id(logged_in_user, int(diary_id))

    if diary:
        print("\n다이어리 정보:")
        print(f"제목: {diary['Title']}, 날짜: {diary['Date']}, 날씨: {diary['Weather']}, 기분: {diary['Mood']}")
        print("내용:", diary['Content'])

        new_title = input("\n새로운 제목을 입력하세요 (변경하지 않을 경우 엔터): ")
        new_content = input("새로운 내용을 입력하세요 (변경하지 않을 경우 엔터): ")

        # update_diary 함수 호출 시 logged_in_user, diary_id, new_title, new_content를 전달
        update_diary(logged_in_user, int(diary_id), new_title, new_content)
        print("다이어리가 성공적으로 수정되었습니다.")
    else:
        print("해당 ID의 다이어리가 존재하지 않습니다.")


def delete_diary(logged_in_user):
    user_diaries = fetch_user_diaries(logged_in_user)

    if not user_diaries:
        print("데이터가 없습니다.")
        return

    print("\n사용자의 다이어리 목록:")
    for diary in user_diaries:
        print(f"다이어리 ID: {diary[0]}, 제목: {diary[1]}, 날짜: {diary[2]}")

    diary_id = input("삭제할 다이어리의 ID를 입력하세요: ")
    diary = fetch_diary_by_id(logged_in_user, diary_id)
    
    if diary:
        print("\n다이어리 정보:")
        print(f"제목: {diary.get('Title')}, 날짜: {diary.get('Date')}, 날씨: {diary.get('Weather')}, 기분: {diary.get('Mood')}")
        print("내용:", diary.get('Content'))

        confirmation = input("\n정말로 삭제하시겠습니까? (y/n): ")
        if confirmation.lower() == "y":
            delete_diary_by_id(logged_in_user, diary_id)  # diary_id를 전달
            print("다이어리가 성공적으로 삭제되었습니다.")
        else:
            print("다이어리 삭제가 취소되었습니다.")
    else:
        print("해당 ID의 다이어리가 존재하지 않습니다.")

def add_category(logged_in_user):
    print("새로운 카테고리를 추가합니다.")
    new_category = input("추가할 카테고리의 이름을 입력하세요: ")

    cursor.execute("INSERT INTO Category (CategoryName, UserID) VALUES (?, ?)", new_category, logged_in_user.UserID)
    conn.commit()

    print(f"카테고리 '{new_category}'가 성공적으로 추가되었습니다.")

def select_category(logged_in_user):
    cursor.execute("SELECT CategoryName FROM Category WHERE UserID = ?", logged_in_user.UserID)
    categories = [row.CategoryName for row in cursor.fetchall()]

    if not categories:
        print("등록된 카테고리가 없습니다. 먼저 카테고리를 추가하세요.")
        return None

    print("다이어리의 카테고리를 선택하세요:")
    for i, category in enumerate(categories, start=1):
        print(f"{i}. {category}")

    category_choice = input("선택하세요 (숫자): ")

    try:
        category_index = int(category_choice) - 1
        selected_category = categories[category_index]
        return selected_category
    except (ValueError, IndexError):
        print("올바른 선택이 아닙니다.")
        return None

def delete_category(logged_in_user):
    selected_category = select_category(logged_in_user)

    if selected_category:
        confirmation = input(f"정말로 카테고리 '{selected_category}'를 삭제하시겠습니까? (y/n): ")

        if confirmation.lower() == "y":
            cursor.execute("DELETE FROM Category WHERE CategoryName = ? AND UserID = ?", selected_category, logged_in_user.UserID)
            conn.commit()
            print(f"카테고리 '{selected_category}'가 성공적으로 삭제되었습니다.")
        else:
            print("카테고리 삭제가 취소되었습니다.")



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
                카테고리는 5을 입력해 추가 가능합니다. 
                *********************************************

                1. 다이어리 작성
                2. 다이어리 조회
                3. 다이어리 수정
                4. 다이어리 삭제
                5. 카테고리 추가
                6. 카테고리 삭제
                7. 로그아웃

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
                    add_category(logged_in_user)
                    pass
                elif diary_choice == "6":
                    delete_category(logged_in_user)
                    pass
                elif diary_choice == "7":
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
