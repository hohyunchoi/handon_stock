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
        print('000')
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

def checkorder(**key):
    conn = connections()
    cursor = conn.cursor()
    sql_sellorder = "select so_num, so_ju, code, mem_code,so_remainju,so_price,so_state from stock_order where so_state = :so_state and code=:code and so_price = :price and so_date = (select min(so_date) from stock_order where code=:code and so_price = :price)"
    try:
        cursor.execute(sql_sellorder, code=key['code'],price=key['price'],so_state=key['state'])
    except Exception as e:
        print('출력 오류', e)
    finally:
        so_ju = cursor.fetchall()
        print('so_ju=', so_ju)
        cursor.close()
        conn.close()
    return so_ju

def selectso_num():
    conn = connections()
    cursor = conn.cursor()
    sql_sonum = "select stock_order_seq.nextVal from dual"
    try:
        cursor.execute(sql_sonum)
        conn.commit()
    except Exception as e:
        print('출력 오류', e)
    finally:
        so_num = cursor.fetchall()[0][0]
        cursor.close()
        conn.close()
    return so_num

def order(**key):
    conn = connections()
    cursor = conn.cursor()
    sql_order = 'insert into stock_order values(:so_num,:code,:mem_code,:stock,:remainju,:price,:state,sysdate)'
    try:
        cursor.execute(sql_order, so_num=key['so_num'],code=key['code'], mem_code=key['mem_code'],stock=key['stock'],price=key['price'],remainju=key['remainju'],state=key['state'])
        conn.commit()
    except Exception as e:
        print('입력 오류', e, key['code'], key['mem_code'],key['stock'],key['price'])
    finally:
        cursor.close()
        conn.close()

def delorder(**key):
    conn = connections()
    cursor = conn.cursor()
    sql_delorder = 'delete stock_order where so_num = :so_num'
    try:
        cursor.execute(sql_delorder,so_num=key['so_num'])
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

def addlog(**key):
    conn = connections()
    cursor = conn.cursor()
    sql_addlog = 'insert into stock_log values(stock_log_seq.nextVal,:code,:buy_mem,:sell_mem,:price,:stock,sysdate)'
    try:
        cursor.execute(sql_addlog,code=key['code'], buy_mem=key['buy_mem'],sell_mem=key['sell_mem'], stock=key['stock'], price=key['price'])
        conn.commit()
    except Exception as e:
        print('입력 오류', e, key['code'], key['mem_code'], key['stock'], key['price'])
    finally:
        cursor.close()
        conn.close()

def checkwallet(**key):
    conn = connections()
    cursor = conn.cursor()
    sql_checkwallet = "select count(*) from stock_wallet where code = :code and mem_code= :mem_code"
    try:
        cursor.execute(sql_checkwallet, code=key['code'], mem_code=key['mem_code'])
    except Exception as e:
        print('출력 오류', e)
    finally:
        check = cursor.fetchall()[0][0]
        cursor.close()
        conn.close()
    return check

def updatestock(**key):
    conn = connections()
    cursor = conn.cursor()
    sql_addlog = 'update stock_wallet set sw_ju = sw_ju + :stocka , sw_orderju = sw_orderju + :stockb , sw_price = sw_price + :price where code = :code and mem_code = :mem_code'
    try:
        cursor.execute(sql_addlog,code=key['code'], stocka=key['stock'],stockb=key['stock'], mem_code=key['mem_code'],price=key['price'])
        conn.commit()
    except Exception as e:
        print('입력 오류', e, key['code'],key['stock'])
    finally:
        cursor.close()
        conn.close()

def addstock(**key):
    conn = connections()
    cursor = conn.cursor()
    sql_addlog = 'insert into stock_wallet values(stock_wallet_seq.nextVal,:mem_code,:code,:price,:stock,:stock)'
    try:
        cursor.execute(sql_addlog, code=key['code'], mem_code=key['mem_code'], stock=key['stock'], price=key['price'])
        conn.commit()
    except Exception as e:
        print('입력 오류', e, key['code'], key['mem_code'], key['stock'], key['price'])
    finally:
        cursor.close()
        conn.close()

def accountout(**key):
    conn = connections()
    cursor = conn.cursor()
    sql_login = """update account set ac_balance = ac_balance  - :price
                    where ac_code = 
                    (select a.ac_code
                     from account_client ac, account a 
                     where ac.ac_code = a.ac_code and ac.mem_code =:mem_code and ac.pro_code=6)"""
    try:
        cursor.execute(sql_login, mem_code=key['mem_code'],price=key['price'])
        conn.commit()
    except Exception as e:
        print('출력 오류', e)
    finally:
        cursor.close()
        conn.close()

def accountin(**key):
    conn = connections()
    cursor = conn.cursor()
    sql_login = """update account set ac_balance = ac_balance  + :price
                        where ac_code = 
                        (select a.ac_code
                         from account_client ac, account a 
                         where ac.ac_code = a.ac_code and ac.mem_code =:mem_code and ac.pro_code=6)"""
    try:
        cursor.execute(sql_login, mem_code=key['mem_code'], price=key['price'])
        conn.commit()
    except Exception as e:
        print('출력 오류', e)
    finally:
        cursor.close()
        conn.close()


def delorder(**key):
    conn = connections()
    cursor = conn.cursor()
    sql_addlog = 'delete stock_order where so_num = :so_num'
    try:
        cursor.execute(sql_addlog, so_num = key['so_num'])
        conn.commit()
    except Exception as e:
        print('입력 오류', e, key['so_num'])
    finally:
        cursor.close()
        conn.close()

def orderupdate(**key):
    conn = connections()
    cursor = conn.cursor()
    sql_orderup = "update stock_order set so_remainju = so_remainju - :stock where so_num = :so_num "
    try:
        cursor.execute(sql_orderup, stock=key['stock'],so_num=key['so_num'])
        conn.commit()
    except Exception as e:
        print('출력 오류', e)
    finally:
        print(type(key['stock']))
        print(type(key['so_num']))
        print('stock=',key['stock'])
        print('so_num=',key['so_num'])
        print('왜 앙대?')
        cursor.close()
        conn.close()

def selwalletstock(**key):
    conn = connections()
    cursor = conn.cursor()
    sql_sonum = "select sw_ju,sw_price,sw_orderju from stock_wallet where mem_code = :mem_code and code = :code"
    try:
        cursor.execute(sql_sonum,mem_code=key['mem_code'],code=key['code'])
    except Exception as e:
        print('출력 오류', e)
    finally:
        sw_ju = cursor.fetchall()
        print('111111111111111122')
        print(sw_ju)
        cursor.close()
        conn.close()
    return sw_ju

def delwalletstock(**key):
    conn = connections()
    cursor = conn.cursor()
    sql_addlog = 'delete stock_wallet where code = :code'
    try:
        cursor.execute(sql_addlog, code=key['code'])
        conn.commit()
    except Exception as e:
        print('입력 오류', e)
    finally:
        cursor.close()
        conn.close()

def upwalletstock(**key):
    conn = connections()
    cursor = conn.cursor()
    sql_login = "update stock_wallet set sw_ju = sw_ju - :stock , sw_price = round(sw_price - (sw_price/sw_ju)*:stock,0) where mem_code= :mem_code and code = :code"
    try:
        cursor.execute(sql_login,mem_code=key['mem_code'],code=key['code'],stock=key['stock'])
        conn.commit();
    except Exception as e:
        print('출력 오류', e)
    finally:
        cursor.close()
        conn.close()

def upwalletstocksell(**key):
    conn = connections()
    cursor = conn.cursor()
    sql_login = "update stock_wallet set sw_ju = sw_ju - :stock , sw_price = round(sw_price - (sw_price/sw_ju)*:stock,0), sw_orderju = sw_orderju-:stock where mem_code= :mem_code and code = :code"
    try:
        cursor.execute(sql_login, mem_code=key['mem_code'], code=key['code'], stock=key['stock'])
        conn.commit();
    except Exception as e:
        print('출력 오류', e)
    finally:
        print(key['stock'],': 11')
        cursor.close()
        conn.close()

def upwalletorderju(**key):

    conn = connections()
    cursor = conn.cursor()
    sql_login = "update stock_wallet set sw_orderju = sw_orderju-:stock where mem_code= :mem_code and code = :code"
    try:
        cursor.execute(sql_login, mem_code=key['mem_code'], code=key['code'], stock=key['stock'])
        conn.commit();
    except Exception as e:
        print('출력 오류', e)
    finally:
        cursor.close()
        conn.close()

def selstockwallet(mem_code):
    conn = connections()
    cursor = conn.cursor()
    sql_sonum = "select sw_num,mem_code,code,sw_price,sw_ju,sw_orderju from stock_wallet where mem_code=:mem_code"
    try:
        cursor.execute(sql_sonum, mem_code=mem_code)
    except Exception as e:
        print('출력 오류', e)
    finally:
        sw = cursor.fetchall()
        print('12121212121212121212')
        print('sw=',sw)
        print('mem_code=',mem_code)
        cursor.close()
        conn.close()
    return sw

def selstockname(code):
    conn = connections()
    cursor = conn.cursor()
    sql_sonum = "select name from stock_code where code=:code"
    try:
        cursor.execute(sql_sonum, code=code)
    except Exception as e:
        print('출력 오류', e)
    finally:
        code = cursor.fetchall()[0][0]
        print(code)
        cursor.close()
        conn.close()
    return code