from django.shortcuts import render, redirect,HttpResponseRedirect, HttpResponse
from stock import models
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from bs4 import BeautifulSoup as bs
import pandas as pd
import requests as rq
from django.db import transaction
import json
from collections import OrderedDict
import random
from selenium import webdriver
'''
driver = webdriver.Chrome('C:\ikosmo64\chromedriver.exe')
driver.get('https://www.ktb.co.kr/trading/popup/itemPop.jspx')
#driver.find_element_by_class_name('txt_s')
html = driver.page_source
soup = bs(html, 'html.parser')
code = soup.select('.tbody_content > tr > td:first-child')
name= soup.select('.tbody_content > tr > td:last-child')
codelist= []
for i in code:
    codelist.append(i.text)
namelist = []
for i in name:
    namelist.append(i.text.rstrip())
for code,name in zip(codelist,namelist):
    addcode(code=code,name=name)

create table stock_code(
c_num number primary key,
code varchar2(10),
name varchar2(90));
create sequence stock_code_seq
increment by 1
start with 1;
    '''


@csrf_exempt
def login(request):
    if 'user' in request.session:
        return redirect("home")
    else:
        if request.method == 'POST':
            emailv = request.POST['email']
            pwv = request.POST['pw']
            if models.idcheck(email=emailv, pw=pwv):
                profile = models.login(email=emailv, pw=pwv)[0]
                request.session['user'] = profile
                if models.account(mem_code=request.session['user'][0])==[]:
                    return redirect("createaccount")
                else:
                    request.session['account'] = models.account(mem_code=request.session['user'][0])[0]
                    return redirect("home")
            else:
                msg = "아이디 및 비밀번호를 확인해주세요."
                return render(request, "loginform.html", {"msg": msg})
        else:
            return render(request, "loginform.html")

@csrf_exempt
@transaction.atomic
def createaccount(request):
    if request.method == 'POST':
        ac_pwd = request.POST['pw1']
        ac_name = request.POST['name']
        a = 1
        ac_num = "100"
        while a==1:
            for i in range(1, 8):
                ac_num += str(random.randrange(0, 10))
            a = models.selac_num(ac_num=ac_num)
        models.addaccount(ac_num=ac_num,ac_name=ac_name,ac_pwd=ac_pwd)

        ac_code = models.selac_code(ac_num=ac_num)
        models.addaccountclient(ac_code=ac_code,mem_code=request.session['user'][0])
        request.session['account'] = models.account(mem_code=request.session['user'][0])[0]
        return redirect("home")
    else:
        return render(request,"createaccount.html")


@csrf_exempt
def join(request):
    return render(request, "loginform.html")


def home(request):
    profile = request.session.get("user")
    return render(request, "stockmain.html", {"profile": profile})

def logout(request):
    if 'user' in request.session:
        del request.session["user"]
        return redirect("login")
    else:
        return redirect("login")


def account(request):
    mem_code = request.session.get("user")[0]
    account = models.account(mem_code=mem_code)
    accountmap = {"ac_num": account[0][0], "ac_balance": account[0][1]}
    return render(request, "account.html", {"account": accountmap})


def getNaverStockData(**key):
    url = 'https://finance.naver.com/sise/sise_market_sum.nhn?sosok=' + key['sosok'] + '&page=' + str(key["page"])
    result = pd.read_html(url, encoding="euc-kr")[1]
    result = result.iloc[:, :-8].dropna().reset_index(drop=True)
    result['N'] = result['N'].astype(int)
    result['현재가'] = result['현재가'].astype(int)
    result['전일비'] = result['전일비'].astype(int)
    return result


def getPaging(**key):
    url = 'https://finance.naver.com/sise/sise_market_sum.nhn'
    site = rq.get(url)
    site2 = site.content.decode('euc-kr')
    soup = bs(site2, 'html.parser')
    page = soup.select('.Nnavi')
    return page


def getlastpage(request, **key):
    url = 'https://finance.naver.com/sise/sise_market_sum.nhn?sosok=' + key['sosok'] + '&page=100'
    site = rq.get(url)
    site2 = site.content.decode('euc-kr')
    soup = bs(site2, 'html.parser')
    lastpage = soup.select('td.on > a')[0].text
    return int(lastpage)


def stockchart(request):
    page = request.GET['page']
    sosok = request.GET['sosok']
    return render(request, "stockchart.html", {"page": page, "sosok": sosok})


def stockchartajax(request):
    page = request.GET['page']
    sosok = request.GET['sosok']
    stockchart = getNaverStockData(page=page, sosok=sosok).to_html(index=False)
    return render(request, "stockchartserver.html", {"stockchart": stockchart})


def pagingajax(request):
    page = request.GET['page']
    pages = getPaging(page=page)[0]
    return render(request, "pagingserver.html", {"page": str(pages)})


def paging(request):
    page = int(request.GET['page'])
    sosok = request.GET['sosok']
    startpage = 0
    endpage = 0
    lastpagev = int(getlastpage(request, sosok=sosok))
    if (page - 5) < 1:
        startpage = 1
    else:
        startpage = page - 5
        if startpage > (lastpagev - 10):
            startpage = lastpagev - 10
    if (page + 5) > lastpagev:
        endpage = lastpagev
    else:
        endpage = page + 5
        if endpage < 10:
            endpage = 10
    pages = '<table><tr>'
    if page != 1:
        pages += '<td><a href="stockchart?sosok=' + sosok + '&page=1"><<</td>'
        if page < 11:

            pages += '<td><a href="stockchart?sosok=' + sosok + '&page=1"><</td>'
        else:
            pages += '<td><a href="stockchart?sosok=' + sosok + '&page=' + str(page - 10) + '"><</td>'
    for i in range(startpage, endpage + 1):
        if i == page:
            pages += '<td><strong>' + str(i) + '</strong>'
        else:
            pages += '<td><a href="stockchart?sosok=' + sosok + '&page=' + str(i) + '">' + str(i) + '</a></td>'
    if page != lastpagev:

        if page > lastpagev - 10:
            pages += '<td><a href="stockchart?sosok=' + sosok + '&page=' + str(lastpagev) + '">></td>'
        else:
            pages += '<td><a href="stockchart?sosok=' + sosok + '&page=' + str(page + 10) + '">></td>'
        pages += '<td><a href="stockchart?sosok=' + sosok + '&page=' + str(lastpagev) + '">>></td>'
    pages += '</tr></table>'
    return render(request, "pagingserver.html", {"page": pages})


def stockdetail(request):
    name = request.GET['name']

    code = models.getcode(name=name)
    if code == []:
        return render(request, "stockmain.html",{"msg":"이름을 확인해주세요."})
    else:
        code = code[0][0]
    request.session['code'] = code
    sosok=''
    if "sosok" in request.GET:
        sosok = request.GET['sosok']

    else:
        url = 'https://finance.naver.com/item/main.nhn?code='+code
        site = rq.get(url)
        site2 = site.content.decode('euc-kr')
        soup = bs(site2, 'html.parser')
        if soup.select('.kospi')==[]:
            sosok = 'KOSDAQ'
        else:
            sosok = 'KOSPI'
    request.session['name'] = name

    """df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]
    code = str(df[df['회사명'] == name]['종목코드'].values[0])
    code = code.zfill(6)"""
    if sosok == '0':
        sosok = 'KOSPI'
    elif sosok =='1':
        sosok = 'KOSDAQ'
    request.session['sosok'] = sosok

    return render(request, "stockdetail.html", {"name": name, "code": code, 'sosok': sosok})


def today(request):
    code = request.GET['code']
    url = 'https://finance.naver.com/item/main.nhn?code=' + code
    site = rq.get(url)
    site2 = site.content.decode('euc-kr')
    soup = bs(site2, 'html.parser')
    price = soup.select('.no_today .blind')[0].text
    priceupdown = soup.select('.no_exday .blind')[0].text
    priceper = soup.select('.no_exday .blind')[1].text
    yesterday = soup.select('.no_info .blind')[0].text
    pricemax = soup.select('.no_info .blind')[1].text
    dill = soup.select('.no_info .blind')[3].text
    pricesiga = soup.select('.no_info .blind')[4].text
    pricemin = soup.select('.no_info .blind')[5].text
    dillprice = soup.select('.no_info .blind')[6].text
    updown = soup.select('.no_exday .ico')[0].text
    color = ''
    if updown == '상승':
        priceper = '+' + priceper + '%'
        priceupdown = '▲' + priceupdown
        color = 'red'
    elif updown == '하락':
        priceper = '-' + priceper + '%'
        color = 'blue'
        priceupdown = '▼' + priceupdown
    else:
        color = 'gary'

    yesterdayint = int(''.join(yesterday.split(',')))
    maxint = int(''.join(pricemax.split(',')))
    minint = int(''.join(pricemin.split(',')))
    sigaint = int(''.join(pricesiga.split(',')))
    maxcolor = ''
    if yesterdayint > maxint:
        maxcolor = 'blue'
    elif yesterdayint < maxint:
        maxcolor = 'red'
    else:
        maxcolor = 'black'
    mincolor = ''
    if yesterdayint > minint:
        mincolor = 'blue'
    elif yesterdayint < minint:
        mincolor = 'red'
    else:
        mincolor = 'black'
    sigacolor = ''
    if yesterdayint > sigaint:
        sigacolor = 'blue'
    elif yesterdayint < sigaint:
        sigacolor = 'red'
    else:
        sigacolor = 'black'
    chart = soup.select('#img_chart_area')[0]['src']
    date = soup.select('.date')[0].text
    hoga = str(soup.select('#tab_con2 > table')[0])
    hogatable = gethogatable(request, code)

    return render(request, "stocktodayserver.html",
                  {"price": price, "priceupdown": priceupdown, "priceper": priceper, "yesterday": yesterday,
                   "pricemax": pricemax,
                   "dill": dill, "pricesiga": pricesiga, "pricemin": pricemin, "updown": updown, "dillprice": dillprice,
                   "chart": chart, 'maxcolor': maxcolor, 'mincolor': mincolor, 'sigacolor': sigacolor,
                   'color': color, 'date': date, "hoga": hogatable})


def gethogatable(request, code):
    url = 'https://finance.naver.com/item/main.nhn?code=' + code
    site = rq.get(url)
    site2 = site.content.decode('euc-kr')
    soup = bs(site2, 'html.parser')
    hogamax = []
    tdown = soup.select('tr.total > td.f_down')[0].text.replace("\n", "").replace('\t', "")
    tup = soup.select('tr.total > td.f_up')[0].text.replace("\n", "").replace('\t', "")
    dealay = soup.select('.txt_color')[0].text
    for i in range(5, 10):
        hoga1 =0
        if ''.join(
            soup.select('#tab_con2 > table .f_down td:nth-child(1)')[i].text.replace('\n', "").replace('\t', "").replace('\xa0',"").split(
                ',')) != '':
            hoga1 = int(''.join(
                soup.select('#tab_con2 > table .f_down td:nth-child(1)')[i].text.replace('\n', "").replace('\t', "").replace('\xa0',"").split(
                    ',')))
        hogamax.append(hoga1)
    for i in range(0, 5):
        hoga2 =0
        if ''.join(
            soup.select('#tab_con2 > table .f_up td:nth-child(3)')[i].text.replace('\n', "").replace('\t', "").replace('\xa0',"").split(
                ',')) !='':
            hoga2 = int(''.join(
                soup.select('#tab_con2 > table .f_up td:nth-child(3)')[i].text.replace('\n', "").replace('\t', "").replace('\xa0',"").split(
                    ',')))

        hogamax.append(hoga2)
    hogatable = '<table class="hoga"><thead><tr><td>매도잔량</td><td>호가</td><td>매수잔량</td></tr><thead><tfoot><tr><td>' + tdown + '</td><td>잔량합계<br><span>' + dealay + '</span></td><td>' + tup + '</td></tr></tfoot><tbody>'
    for i in range(5, 10):
        hoga1 = soup.select('#tab_con2 > table .f_down td:nth-child(1)')[i].text
        hoga2 = soup.select('#tab_con2 > table .f_down td:nth-child(2)')[i].text
        hogatable += '<tr class="f_down"><td><div class="grp"><div style="width:' + str(
            int((int(hogamax[i - 5]) / max(hogamax)) * 100)) + '%;">' + str(
            hoga1) + '</div></div></td><td>' + str(hoga2) + '</td><td></td></tr>'

    for i in range(0, 5):
        hoga1 = soup.select('#tab_con2 > table .f_up td:nth-child(2)')[i].text
        hoga2 = soup.select('#tab_con2 > table .f_up td:nth-child(3)')[i].text
        if hogamax[i+5] != '':
            hogatable += '<tr class="f_up"><td></td><td>' + str(
                hoga1) + '</td><td><div class="grp"><div style="width:' + str(
                int((hogamax[i + 5] / max(hogamax)) * 100)) + '%;">' + str(hoga2) + '</div></td></tr>'
    hogatable += '</tbody></table>'
    request.session['hogatable'] = hogatable
    return hogatable


def order(request):
    if "name" in request.session:
        name = request.session['name']
        sosok = request.session['sosok']
        code = request.session['code']
    else:
        name = '삼성전자'
        sosok = 'KOSPI'
        code = '005930'
    hogatable = gethogatable(request, code)
    soup = bs(hogatable, 'html.parser')
    f_down = soup.select('.f_down td:nth-child(2)')[4].text
    f_down = f_down.replace("\n", "").replace('\t', "")
    f_up = soup.select('.f_up td:nth-child(2)')[0].text
    f_up = f_up.replace("\n", "").replace('\t', "")

    return render(request, "stockorder.html",
                  {"name": name, "code": code, "sosok": sosok, "f_down": f_down, "f_up": f_up})


def hogatable(request):
    code = request.GET['code']
    hogatable = request.session['hogatable']
    return render(request, "hogatableserver.html", {"hogatable": hogatable})

@csrf_exempt
@transaction.atomic
def buyorder(requset):
    balance = int(requset.session['account'][1])
    stock = int(requset.POST['stock'])
    price = int(requset.POST['price'])
    code = requset.POST['code']
    sellprice = int(requset.POST['sellprice'])
    mem_code= requset.session['user'][0]
    so_num = models.selectso_num()
    # 계좌 잔고와 사고자하는 잔고 비교
    stocktoast1 = 0
    stocktoast2 = 0
    msg1 = ''
    msg2 = ''
    if balance > stock*price: # 잔고가 많다면
        #원하는 가격에 판매주문이 있는지 확인
        while stock > 0:
            sellstock = models.checkorder(code=code,price=price,state=1)
            #없으면 호가와 가격 확인
            if sellstock == [] :
                print('판매주문 없음 호가랑 확인!')
                # 판매호가 보다 주문가격이 높으면
                if price >= sellprice:
                    print('호가로 거래 바로 실행!')
                    # 구매로그 남기기
                    print('구매로그!!')
                    models.addlog(code=code, buy_mem=mem_code,sell_mem=-1, stock=stock, price=price*stock)
                    # 주식지갑에 해당 주식이 있는지 없는지 확인
                    # 있으면
                    if models.checkwallet(code=code,mem_code=mem_code) == 1:
                        #기존 주식에 추가
                        print('기존주식에 추가!')
                        models.updatestock(code=code,stock=stock,mem_code=mem_code,price=stock*price)
                    #없으면
                    else:
                        print('새로운 주식 추가!')
                        #새로운 주식 추가
                        models.addstock(code=code,mem_code=mem_code,stock=stock,price=stock*price)
                    msg1 = "주 구매 완료."
                    stocktoast1 += stock

                else:
                    #호가보다 구매주문 가격이 낮으면 구매주문 추가
                    models.order(so_num=so_num,code=code, mem_code=mem_code, stock=stock, price=price,remainju=stock,state=0)
                    stocktoast2 +=stock
                    msg2 = "주 구매주문 완료"
                # 주식계좌에서 돈 빠져나감
                models.accountout(price=stock * price, mem_code=mem_code)
                stock=0

            #같은 가격의 판매 주문이 있다면 매칭
            else:
                print('거래 매치!!!!')
                print(' 주문량이 판매량보다 많음!')
                if stock >= sellstock[0][1]:
                    stock = stock - sellstock[0][1]
                    models.delorder(so_num=sellstock[0][0])
                    models.addlog(code=code, buy_mem=mem_code,sell_mem=sellstock[0][3], stock=sellstock[0][1], price=price*sellstock[0][1])
                    if models.checkwallet(code=code,mem_code=mem_code) == 1:
                        models.updatestock(code=code,stock=sellstock[0][1],mem_code=mem_code,price=sellstock[0][1]*price)
                    else:
                        models.addstock(code=code,mem_code=mem_code,stock=sellstock[0][1],price=sellstock[0][1]*price)
                    sw_ju = models.selwalletstock(mem_code=sellstock[0][3],code=code)[0][0]
                    if (sw_ju - stock) == 0:
                        models.delwalletstock(code=code,mem_code=sellstock[0][3])
                    else:
                        models.upwalletstock(code=code,mem_code=sellstock[0][3],stock=sellstock[0][1])
                    models.accountout(price=sellstock[0][1] * price, mem_code=mem_code)
                    models.accountin(price=sellstock[0][1] * price, mem_code=sellstock[0][3])
                    stocktoast1 += sellstock[0][1]
                    msg1 = "주 구매 완료."

                # 주문량이 판매주문량보다 적거나 같을 경우
                else:
                    print('판매량이 더 많음!!!')
                    print(sellstock[0][3])
                    #판매주문의 수량 제거
                    print(sellstock[0][0])

                    print('이게 안됨')
                    models.orderupdate(so_num=sellstock[0][0],stock=stock)
                    #로그남기기
                    models.addlog(code=code, buy_mem=mem_code, sell_mem=sellstock[0][3], stock=stock, price=price*stock)
                    #판매자 주식 지갑 비우기
                    #sw_ju = models.selwalletstock(mem_code=sellstock[0][3],code=code)[0][0]
                    #sw_price = models.selwalletstock(mem_code=sellstock[0][3],code=code)[0][1]
                    #sw_ju = sw_ju-stock
                    #sw_price= sw_price - (sw_price/sw_ju)*stock
                    print('이게 안됨')
                    models.upwalletstock(code=code, mem_code=sellstock[0][3], stock=stock)
                    print('어디냐!!')
                    #구매자 주식 지갑 채우기

                    if models.checkwallet(code=code,mem_code=mem_code) == 1:
                        #기존 주식에 추가
                        print('기존주식에 추가!')
                        models.updatestock(code=code,stock=stock,mem_code=mem_code,price=stock*price)
                    #없으면
                    else:
                        print('새로운 주식 추가!')
                        #새로운 주식 추가
                        models.addstock(code=code,mem_code=mem_code,stock=stock,price=stock*price)
                    # 구매자 계좌 돈 빼기
                    models.accountout(price=stock * price, mem_code=mem_code)
                    #판매자 계좌에 돈 넣기
                    models.accountin(price=stock * price, mem_code=sellstock[0][3])
                    stocktoast1 +=stock
                    msg1 ="주 구매 완료."
                    stock=0
    else:
        return render(requset,"orderserver.html",{"msg":"잔고를 확인해 주세요."})
    msg = ''
    if stocktoast1 != 0:
        msg += str(stocktoast1)+msg1
    if msg2 != '':
        msg += "\n"+str(stocktoast2)+msg2

    return render(requset,"orderserver.html",{"msg":msg})


@csrf_exempt
@transaction.atomic
def sellorder(request):
    stock = int(request.POST['stock'])
    price = int(request.POST['price'])
    code = request.POST['code']
    buyprice = int(request.POST['buyprice'])
    print('buyprice?',buyprice)
    print('price?', price)
    mem_code = request.session['user'][0]
    so_num = models.selectso_num()
    print(models.selwalletstock(mem_code=mem_code,code=code))

    stockbalance = models.selwalletstock(mem_code=mem_code,code=code)
    if stockbalance == []:
        return render(request,"orderserver.html",{"msg":"주식이 존재하지 않습니다."})
    else:
        stockbalance = stockbalance[0][2]
    print('주식잔고 = ',stockbalance)
    stocktoast1 = 0
    stocktoast2 = 0
    msg1 = ''
    msg2 = ''
    #주식 잔고가 판매주문량보다 많으면
    if stockbalance >= stock:
        print('주식잔고가 더 많다!')
        #구매주문 확인
        while stock>0:
            buystock = models.checkorder(code=code, price=price,state=0)
            #구매주문 없으면
            if buystock == []:
                print('구매주문 없음 호가랑 비교')
                # 판매가격이  호가사는 가격보다 낮다면
                if price <= buyprice:
                    print('호가로 거래 바로 실행!')
                    #판매로그 남기기
                    print('판매로그')
                    models.addlog(code=code, buy_mem=-1, sell_mem=mem_code, stock=stock, price=price*stock)

                    #주식지갑에서 판매가능주식, 주식 빼기
                    models.upwalletstocksell(mem_code=mem_code,stock=stock,code=code)

                    #주식계좌에 돈 추가
                    models.accountin(mem_code=mem_code,price=price*stock)
                    msg1 = '주 판매 완료.'
                    stocktoast1 += stock
                # 판매가격이 호가사는 가격보다 높다면
                else:
                    #주문넣기
                    models.order(so_num=so_num, code=code, mem_code=mem_code, stock=stock, price=price, remainju=stock,state=1)
                    #orderju 낮추기
                    models.upwalletorderju(code=code, mem_code=mem_code, stock=stock)
                    msg2 = '주 판매주문 완료.'
                    stocktoast2 += stock

                stock=0
            #구매주문 있으면
            else:
                print('거래매칭!!!')
                # 팔고싶은 수량이랑 구매 수량이랑 비교
                if stock >= buystock[0][1]:
                    print('판매량이 더 많다 지워!!')
                    #판매량 - 구매주문량
                    stock = stock - buystock[0][1]
                    #구매주문삭제
                    models.delorder(so_num=buystock[0][0])
                    #로그남기기
                    models.addlog(code=code, buy_mem=buystock[0][3], sell_mem=mem_code, stock=buystock[0][1], price=price*buystock[0][1])
                    #주식지갑에서 주식 빼기
                    models.upwalletstocksell(mem_code=mem_code, stock=buystock[0][1], code=code)
                    #판매자 지갑에 돈 넣기
                    models.accountin(price=buystock[0][1] * price, mem_code=mem_code)
                    #구매자 주식지갑에 주식 넣기
                    # 주식있는지 없는지
                    if models.checkwallet(code=code, mem_code=buystock[0][3]) == 1:
                        # 기존 주식에 추가
                        print('기존주식에 추가!')
                        models.updatestock(code=code, stock=buystock[0][1], mem_code=buystock[0][3],
                                           price=buystock[0][1] * price)
                    # 없으면
                    else:
                        print('새로운 주식 추가!')
                        # 새로운 주식 추가
                        models.addstock(code=code, mem_code=buystock[0][3], stock=buystock[0][1], price=buystock[0][1] * price)
                    msg1 = '주 판매 완료.'
                    stocktoast1 += buystock[0][1]
                # 판매주문량보다 구매주문량이 크면
                else:
                    print('구매량이 더많다!! 구매주문 업데이트만!')
                    #주문 수량 지우기
                    models.orderupdate(so_num=buystock[0][0],stock=stock)
                    #로그남기기
                    models.addlog(code=code, buy_mem=buystock[0][3], sell_mem=mem_code, stock=stock, price=price*buystock[0][1])
                    #판매자 주식지갑 비우기
                    models.upwalletstocksell(code=code, mem_code=mem_code, stock=stock)
                    #구매자 주식지갑 넣어주기
                    if models.checkwallet(code=code, mem_code=buystock[0][3]) == 1:
                        # 기존 주식에 추가
                        print('기존주식에 추가!')
                        models.updatestock(code=code, stock=buystock[0][1], mem_code=buystock[0][3],
                                           price=buystock[0][1] * price)
                    # 없으면
                    else:
                        print('새로운 주식 추가!')
                        # 새로운 주식 추가
                        models.addstock(code=code, mem_code=buystock[0][3], stock=buystock[0][1], price=buystock[0][1] * price)

                    #판매자 돈들어오기
                    models.accountin(price=stock * price, mem_code=mem_code)
                    msg1 = '주 판매 완료.'
                    stocktoast1 += stock
                    stock = 0
        if models.selwalletstock(mem_code=mem_code,code=code)[0][0] == 0:
            models.delwalletstock(code=code,mem_code=mem_code)

    else:
        return render(request,"orderserver.html",{"msg":"거래 가능 주식 수가 부족합니다."})
    msg = ''
    if stocktoast1 != 0:
        msg += str(stocktoast1)+msg1
    if msg2 != '':
        msg += "\n"+str(stocktoast2)+msg2
    return render(request, "orderserver.html",{"msg":msg})

def stockwallet(request):
    mem_code = request.session['user'][0]
    print(mem_code)
    stockwallet = models.selstockwallet(mem_code)
    print(stockwallet)
    sw =[]
    stockwalletcount = models.selcountwallet(mem_code)
    realprice = 0
    buyprice = 0
    print("****************************")
    print(stockwalletcount)
    if stockwalletcount >= 1:
        for i in stockwallet:
            name = models.selstockname(i[2])
            url = 'https://finance.naver.com/item/main.nhn?code=' + i[2]
            site = rq.get(url)
            site2 = site.content.decode('euc-kr')
            soup = bs(site2, 'html.parser')
            updown = soup.select('.no_exday .ico')[0].text
            color = ''
            priceupdown = soup.select('.no_exday .blind')[0].text
            priceper = soup.select('.no_exday .blind')[1].text
            nowcolor = ''


            price = soup.select('.no_today .blind')[0].text
            print("프라이스느느느은으능느은",priceupdown)
            print(i[3])
            nowprice = i[4]*int(price.replace(",",""))
            value = nowprice - i[3]
            nowpriceper = round(((nowprice/i[3])*100) - 100,2)
            if nowprice > i[3]:
                nowcolor = "red"
                #value = '▲' + str(value)
                nowpriceper = '+'+str(nowpriceper)+'%'
            elif nowprice < i[3]:
                nowcolor ="blue"
                #value = '▼' + str(value)
                nowpriceper =  str(nowpriceper) + '%'
            else:
                nowcolor="black"

            if updown == '상승':
                priceper = '+' + priceper + '%'
                #priceupdown = '▲' + priceupdown
                color = 'red'
            elif updown == '하락':
                priceper = '-' + priceper + '%'
                color = 'blue'
                #priceupdown = '▼' + priceupdown
            else:
                color = 'black'


            print('가격')
            print(price)
            realprice += nowprice
            buyprice += i[3]
            stock = {"sw_num":i[0],"code":i[2],"sw_price":format(i[3],','),"sw_ju":i[4],"sw_orderju":i[5],"name":name,"priceper":priceper,"priceupdown":priceupdown,"value":format(value,','),
                     "color":color,"price":price,"nowprice":format(nowprice,','),"nowpriceper":nowpriceper,"nowcolor":nowcolor}
            sw.append(stock)
        print(sw)
        realupdown = 0
        realupdownper = 0
        print("리얼 프라이스!!!!!",realprice)
        print("바이 프라이스!!!!!",buyprice)

        realupdown = realprice - buyprice
        realupdownper = round(((realprice - buyprice)/buyprice)*100,2)
        realcolor = 'black'
        if realupdown < 0:
            realcolor = "blue"
        elif realupdown > 0:
            realcolor ="red"
        return render(request,"stockwallet.html",{"sw":sw,"realprice":format(realprice,','),"realupdown":format(realupdown,','),"realupdownper":realupdownper,"realcolor":realcolor})
    else:
        return render(request, "stockwallet.html")

def stockwallet_ajax(request):
    mem_code = request.session['user'][0]

    stockwallet = models.selstockwallet(mem_code)

    sw = []
    realprice = 0
    buyprice = 0

    for i in stockwallet:
        name = models.selstockname(i[2])
        url = 'https://finance.naver.com/item/main.nhn?code=' + i[2]
        site = rq.get(url)
        site2 = site.content.decode('euc-kr')
        soup = bs(site2, 'html.parser')
        updown = soup.select('.no_exday .ico')[0].text
        color = ''
        priceupdown = soup.select('.no_exday .blind')[0].text
        priceper = soup.select('.no_exday .blind')[1].text
        nowcolor = ''

        price = soup.select('.no_today .blind')[0].text

        nowprice = i[4] * int(price.replace(",", ""))
        nowpriceper = round(((nowprice / i[3]) * 100) - 100, 2)
        value = nowprice - i[3]
        if nowprice > i[3]:
            nowcolor = "red"
            #value = '▲' + str(value)
            nowpriceper = '+' + str(nowpriceper) + '%'
        elif nowprice < i[3]:
            nowcolor = "blue"
            #value = '▼' + str(value)
            nowpriceper = str(nowpriceper) + '%'
        else:
            nowcolor = "black"

        if updown == '상승':
            priceper = '+' + priceper + '%'
            #priceupdown = '▲' + priceupdown
            color = 'red'
        elif updown == '하락':
            priceper = '-' + priceper + '%'
            color = 'blue'
            #priceupdown = '▼' + priceupdown
        else:
            color = 'black'

        #stock = OrderedDict()
        #stock["priceper"]= priceper
        #stock["priceupdown"] =priceupdown
        #stock["value"] =value
        #stock["color"] =color
        #stock["price"] =price
        #stock["nowprice"] =nowprice
        #stock["nowpriceper"] =nowpriceper
        #stock["nowcolor"] =nowcolor
        #stock = json.dumps(stock)

        stock = {"priceper": priceper, "priceupdown": priceupdown, "value": value,
                "color": color, "price": price, "nowprice": nowprice, "nowpriceper": nowpriceper, "nowcolor": nowcolor}
        sw.append(stock)

    sw = json.dumps(sw)
    return  render(request,"stockwalletserver.html",{"sw":sw})