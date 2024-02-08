from sqlalchemy import Column,Integer,String,Boolean,DateTime
from pydantic import BaseModel
from db import Base
from db import ENGINE
from datetime import datetime
class UserTable(Base):
    __tablename__ = 'ai_version_w'
    serial=Column(Integer,primary_key=True,autoincrement=True)
    type = Column(String)
    version = Column(String)
    desc= Column(String)
    reg_date = Column(DateTime)
class User(BaseModel):
    type:str
    version:str
    desc:str
    
      
      
      
class FunctionTable(Base):
    __tablename__='function_table'
    name=Column(String,primary_key=True)
    prompt=Column(String)
    result=Column(String)
    action=Column(String)
    type=Column(String)
    data=Column(String)
class fuction_table(BaseModel):
    name:str
    prompt:str
    result:str
    action:str
    type:str
    data:str