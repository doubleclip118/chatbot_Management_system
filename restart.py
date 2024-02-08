import subprocess
from fastapi import FastAPI, File, UploadFile, HTTPException,Depends,status,WebSocket
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
import socket
from starlette.websockets import WebSocketDisconnect
from fastapi.security import  OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import HTMLResponse
from starlette.websockets import WebSocketDisconnect
from websockets.exceptions import ConnectionClosedOK
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from db import session, Base, ENGINE
from models import UserTable, User, FunctionTable, fuction_table
from datetime import datetime

html = """
 <body>
 <h1>WebSocket Chat</h1>
 <form action="" onsubmit="sendMessage(event)">
 <input type="text" id="messageText"
autocomplete="off"/>
 <button>Send</button>
 </form>
 <ul id='messages'></ul>
 <script>
 var ws = new WebSocket("ws://dev.ai.taky.co.kr:8000/ws");
 ws.onmessage = function(event) {
 var messages = document.getElementById('messages')
 var message = document.createElement('li')
 var content = document.createTextNode(event.data)
 message.appendChild(content)
 messages.appendChild(message)
 };
 function sendMessage(event) {
 var input = document.getElementById("messageText")
 ws.send(input.value)
 input.value = ''
 event.preventDefault()
 }
 </script>
 </body>
"""

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

load_dotenv()

SECRET_KEY =os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))

USERNAME = "1123123"
PASSWORD = "1123123123"


class Token(BaseModel):
    access_token: str
    token_type: str
    username: str

class version(BaseModel):
    device:Optional[str]=None
    version: Optional[str] = None
    change: Optional[str] = None

class input(BaseModel):
    check : Optional[str] = None
class output(BaseModel):
    check : Optional[str] = None

# def check_port(host: str, port: int) -> bool:
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         return s.connect_ex((host, port)) == 0



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_db():
    try:
        db = session()
        yield db
    finally:
        db.close()

# def insert_user(db: Session, user_data: User):
#     new_user = UserTable(
#         type = user_data.type
#         version=user_data.version,
#         desc=user_data.desc,
#         reg_date=user_data.reg_date
#     )
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return new_user

def check_port(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None or username != USERNAME:
            raise credentials_exception
        return username  # 사용자 이름 반환
    except JWTError:
        raise credentials_exception

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.post("/restart_server_chatbot", response_model=output)
def restart_server(check: input, current_user: str = Depends(get_current_user)):
    check="서버가 재시작됩니다."
    try:
        # 외부 재시작 스크립트 실행
        subprocess.run(["bash", "chatbot_restart.sh"], check=True)
        return {"check": check}
    except subprocess.CalledProcessError as e:
        return {"error": str(e)}
    
@app.post("/restart_server_recommand", response_model=output)
def restart_server(check: input, current_user: str = Depends(get_current_user)):
    check="서버가 재시작됩니다."
    try:
        # 외부 재시작 스크립트 실행
        subprocess.run(["bash", "restart.sh"], check=True)
        return {"check": check}
    except subprocess.CalledProcessError as e:
        return {"error": str(e)}
    
@app.post("/uploadfile_chatbot")
async def create_upload_file(file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    target_file_path = Path("/home/ubuntu/openai/uploadfile/chatbot.txt")
    # 파일 내용을 읽어서 타겟 파일에 덮어쓰기 (텍스트 모드)
    with target_file_path.open("w", encoding="utf-8" ) as buffer:
        while True:
            data = await file.read(30000)  # 파일을 조각으로 읽기
            if not data:
                break
            buffer.write(data.decode("utf-8"))
    return {"filename": file.filename}

@app.post("/uploadfile_kiosk/{type}")
async def create_upload_file(type:str,file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    target_file_path=Path("/home/ubuntu/openai/uploadfile/error.txt")
    
    if type == 'first':
        target_file_path = Path("/home/ubuntu/openai/uploadfile/kiosk_first.txt")
    elif type == 'menu':
        target_file_path = Path("/home/ubuntu/openai/uploadfile/kiosk_menu.txt")
    elif type == 'payment':
        target_file_path = Path("/home/ubuntu/openai/uploadfile/kiosk_payment.txt")
    elif type == 'login':
        target_file_path = Path("/home/ubuntu/openai/uploadfile/kiosk_login.txt")
    elif type == "orderlist":
        target_file_path = Path("/home/ubuntu/openai/uploadfile/kiosk_login.txt")
    
    # 파일 내용을 읽어서 타겟 파일에 덮어쓰기 (텍스트 모드)
    with target_file_path.open("w", encoding="utf-8") as buffer:
        while True:
            data = await file.read(20000)  # 파일을 조각으로 읽기
            if not data:
                break
            buffer.write(data.decode("utf-8"))
            
    return {"filename": file.filename}

@app.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),):
    # 사용자 이름과 비밀번호 확인
    if USERNAME != form_data.username or PASSWORD != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디와 비밀번호를 다시확인해주세요",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 액세스 토큰 생성
    try:
        # 액세스 토큰 생성
        data = {
            "sub": USERNAME,
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
        return Token(access_token=access_token, token_type="bearer", username=USERNAME)

    except JWTError as e:
        # JWT 토큰 생성 실패 처리
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="토큰 생성 실패"
        )
        
        
@app.get("/check-port/{host}/{port}")
def get_port_status(host: str, port: int, current_user: str = Depends(get_current_user)):
    is_open = check_port(host, port)
    return {"open": is_open} 
        
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # await websocket.accept()
    # try:
    #     while True:
    #         data = await websocket.receive_text()
    #         await websocket.send_text(f"Message text was: {data}")
    # except WebSocketDisconnect:
    #     print("WebSocket disconnected")
        
    await websocket.accept()
    print("웹소켓은 연결")
    try:
        while True:
            host1 = "*"
            host2 = "*"
            port1 = 3330
            port2 = 3331
            port_open1 = check_port(host1, port1)
            port_open2 = check_port(host2, port2)
            await websocket.send_text(f"Port {3334} open: {port_open1}")
            await websocket.send_text(f"Port {3335} open: {port_open2}")
            await asyncio.sleep(5)  # 5초 간격으로 상태 체크
    except WebSocketDisconnect:
        print("Client disconnected")
    except ConnectionClosedOK:
        # 정상적인 연결 종료 시 예외를 무시 로그에 너무 더럽게 남아서 이 방식 사용
        pass
    finally:
        await websocket.close()

@app.get("/get_chatbot_text_file")
async def read_text_file(current_user: str = Depends(get_current_user)):
    file_path = "/home/ubuntu/openai/uploadfile/chatbot.txt"  # 여기에 서버에 있는 텍스트 파일의 경로를 입력하세요.
    return FileResponse(file_path)

@app.get("/get_kiosk_text_file/{type}")
async def read_text_file(type: str ,current_user: str = Depends(get_current_user)):
    file_path = "/home/ubuntu/openai/uploadfile/file.txt"
    print(type)
    if type == "first":
        file_path = Path("/home/ubuntu/openai/uploadfile/kiosk_first.txt")
    elif type == "menu":
        file_path = Path("/home/ubuntu/openai/uploadfile/kiosk_menu.txt")
    elif type == "payment":
        file_path = Path("/home/ubuntu/openai/uploadfile/kiosk_payment.txt")
    elif type == "login":
        file_path = Path("/home/ubuntu/openai/uploadfile/kiosk_login.txt")
    elif type == "orderlist":
        file_path = Path("/home/ubuntu/openai/uploadfile/kiosk_orderlist.txt")
        
    return FileResponse(file_path)


# @app.post("/input_versions")
# def input_versions(current_user: str = Depends(get_current_user)):
#     file_path = "/home/ubuntu/openai/uploadfile/file.txt"  # 여기에 서버에 있는 텍스트 파일의 경로를 입력하세요.
#     return FileResponse(file_path)


@app.post("/c_version")
def create_user(user: User, db: Session = Depends(get_db),current_user: str = Depends(get_current_user)):
    user_data = user.dict()
    
    user_data['reg_date'] = datetime.now()
    db_user = UserTable(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/r_chatbot_version")
def read_recent_users(db: Session = Depends(get_db),current_user: str = Depends(get_current_user)):
    chatbot = db.query(UserTable).filter(UserTable.type == 'chatbot').order_by(UserTable.serial.desc()).all()
    return chatbot
    

@app.get("/r_kiosk_version")
def read_recent_users(db: Session = Depends(get_db),current_user: str = Depends(get_current_user)):
    kiosk_versions = db.query(UserTable).filter(UserTable.type == 'kiosk').order_by(UserTable.serial.desc()).all()
    return kiosk_versions    
    
    
@app.get("/function_select")
def function_select(db: Session = Depends(get_db),current_user: str = Depends(get_current_user)):
    function_entity=db.query(FunctionTable).all()
    # query = session.query(MyModel).filter(MyModel.name == 'old name').update({'name': 'new name'})
    return function_entity

@app.post("/function_update")
def fuction_update(fun:fuction_table,db: Session = Depends(get_db),current_user: str = Depends(get_current_user)):
    existing_fun = db.query(FunctionTable).filter(FunctionTable.name == fun.name).first()
    if existing_fun:
        existing_fun.prompt = fun.prompt
        existing_fun.result = fun.result
        existing_fun.action = fun.action
        existing_fun.type = fun.type
        existing_fun.data = fun.data
        db.commit()
        return "업데이트 완료"
    else:
        return "데이터가 없습니다."
    
    