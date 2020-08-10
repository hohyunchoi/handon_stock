from django.db import models

# Create your models here.
import cx_Oracle as ora





def connections():
    try:
        conn = ora.connect('hd/hd@192.168.0.122:1521/orcl', encoding='utf-8')
    except Exception as e:
        conn = "예외 발생"
        print(conn)
        print(e)
        return
    return conn


def addcode(**key):
    conn= connections()
    cursor = conn.cursor()
    sql_addcode = 'insert into stock_code values(stock_code_seq.nextVal,:code,:name)'
    try:
        cursor.execute(sql_addcode,code=key['code'],name=key['name'])
        conn.commit()
    except Exception as e:
        print('입력 오류', e,key['code'],key['name'])
    finally:
        cursor.close()
        conn.close()


def idcheck(**key):
    conn = connections()
    cursor = conn.cursor()
    sql_idcheck = "select count(*) from member where mem_email = :email and mem_pwd = :pw"
    try:
        cursor.execute(sql_idcheck,email=key['email'],pw=key['pw'])
    except Exception as e:
        print('출력 오류', e)
    finally:
        idcount = cursor.fetchall()
        id = idcount[0][0] == 1
        cursor.close()
        conn.close()
    return id

def login(**key):
    conn = connections()
    cursor = conn.cursor()
    sql_login = """select MEM_CODE, MEM_EMAIL,MEM_PWD, MEM_NAME , MEM_PRI_CHK ,MEM_EMAIL_CHK,MEM_BIRTH,MEM_GENDER,MEM_LOC,MEM_JOB  
                    from member 
                    where mem_email = :email and mem_pwd = :pw"""
    try:
        cursor.execute(sql_login,email=key['email'],pw=key['pw'])
    except Exception as e:
        print('출력 오류', e)
    finally:
        profile = cursor.fetchall()
        print(profile)
        cursor.close()
        conn.close()
    return profile

def account(**key):
    conn = connections()
    cursor = conn.cursor()
    sql_login = """select ac_num, ac_balance 
                    from member m, account_client ac, account a
                    where m.mem_code = ac.mem_code and ac.ac_code = a.ac_code and m.mem_code=:mem_code and ac.pro_code=6"""
    try:
        cursor.execute(sql_login, mem_code=key['mem_code'])
    except Exception as e:
        print('출력 오류', e)
    finally:
        account = cursor.fetchall()
        print(account)
        cursor.close()
        conn.close()
    return account

def getcode(**key):
    conn = connections()
    cursor = conn.cursor()
    sql_code = "select code from stock_code where name = :name"
    try:
        cursor.execute(sql_code,name=key['name'])
    except Exception as e:
        print('출력 오류', e)
    finally:
        code = cursor.fetchall()[0][0]
        print('code=',code)
        cursor.close()
        conn.close()
    return code