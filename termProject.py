import pyodbc

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
                1. 다이어리 작성
                2. 다이어리 수정
                3. 다이어리 삭제
                4. 카테고리 추가
                5. 카테고리 삭제
                6. 로그아웃
                """)
                diary_choice = input("원하는 작업을 선택하세요: ")
                if diary_choice == "1":
                    # 다이어리 작성 기능 추가
                    pass
                elif diary_choice == "2":
                    # 다이어리 수정 기능 추가
                    pass
                elif diary_choice == "3":
                    # 다이어리 삭제 기능 추가
                    pass
                elif diary_choice == "4":
                    # 카테고리 추가 기능 추가
                    pass
                elif diary_choice == "5":
                    # 카테고리 삭제 기능 추가
                    pass
                elif diary_choice == "6":
                    # 로그아웃 기능 추가
                    break
                else:
                    print("올바른 선택이 아닙니다. 다시 선택하세요.")
    elif choice == "3":
        username = input("삭제할 계정명을 입력하세요: ")
        password = input("비밀번호를 입력하세요: ")
        if delete_user(username, password):
            # 회원탈퇴가 성공하면 프로그램 종료하지 않고 계속 진행
            pass
    elif choice == "4":
        break
    else:
        print("올바른 선택이 아닙니다. 다시 선택하세요.")

# 연결 종료
conn.close()
