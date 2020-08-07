from django.shortcuts import render ,redirect
from stock import models
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from bs4 import BeautifulSoup as bs
import pandas as pd
from selenium import webdriver
import requests as rq

@csrf_exempt
def login(request):
    if 'user' in request.session:
        return redirect("home")
    else:
        if request.method == 'POST':
            emailv =request.POST['email']
            pwv = request.POST['pw']
            if models.idcheck(email= emailv,pw=pwv):
                profile = models.login(email=emailv,pw=pwv)[0]
                request.session['user'] = profile
                return redirect("home")
            else:
                msg = "아이디 및 비밀번호를 확인해주세요."
                return render(request, "loginform.html",{"msg":msg})
        else:
            return render(request, "loginform.html")

@csrf_exempt
def join(request):
    return render(request, "loginform.html")

def home(request):
    profile = request.session.get("user")
    return render(request, "stockmain.html",{"profile":profile})

def logout(request):
    if 'user' in request.session:
        del request.session["user"]
        return redirect("login")
    else:
        return redirect("login")

def account(request):
    mem_code = request.session.get("user")[0]
    account = models.account(mem_code=mem_code)
    accountmap = {"ac_num":account[0][0],"ac_balance":account[0][1]}
    return render(request, "account.html", {"account": accountmap})

def getNaverStockData(**key):
    url = 'https://finance.naver.com/sise/sise_market_sum.nhn?sosok='+key['sosok']+'&page='+str(key["page"])
    result = pd.read_html(url, encoding="euc-kr")[1]
    result = result.iloc[:,:-8].dropna().reset_index(drop=True)
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

def getlastpage(request,**key):
    url = 'https://finance.naver.com/sise/sise_market_sum.nhn?sosok='+key['sosok']+'&page=100'
    site = rq.get(url)
    site2 = site.content.decode('euc-kr')
    soup = bs(site2, 'html.parser')
    lastpage = soup.select('td.on > a')[0].text
    return int(lastpage)

def stockchart(request):
    page = request.GET['page']
    sosok = request.GET['sosok']
    return render(request,"stockchart.html",{"page":page,"sosok":sosok})

def stockchartajax(request):
    page = request.GET['page']
    sosok = request.GET['sosok']
    print(sosok)
    stockchart = getNaverStockData(page=page,sosok=sosok).to_html(index=False)
    return render(request,"stockchartserver.html",{"stockchart":stockchart})

def pagingajax(request):
    page = request.GET['page']
    pages = getPaging(page=page)[0]
    return render(request,"pagingserver.html",{"page":str(pages)})

def paging(request):
    page = int(request.GET['page'])
    sosok = request.GET['sosok']
    startpage= 0
    endpage=0
    lastpagev = int(getlastpage(request,sosok=sosok))
    if (page-5)<1:
        startpage = 1
    else:
        startpage = page -5
        if startpage > (lastpagev-10):
            startpage = lastpagev-10
    if (page+5)>lastpagev:
        endpage = lastpagev
    else:
        endpage = page+5
        if endpage <10:
            endpage = 10
    pages = '<table><tr>'
    if page != 1:
        pages += '<td><a href="stockchart?sosok='+sosok+'&page=1"><<</td>'
        if page <11:

            pages += '<td><a href="stockchart?sosok='+sosok+'&page=1"><</td>'
        else:
            pages += '<td><a href="stockchart?sosok='+sosok+'&page='+str(page-10)+'"><</td>'
    for i in range(startpage,endpage+1):
        if i == page:
            pages += '<td><strong>'+str(i)+'</strong>'
        else:
            pages += '<td><a href="stockchart?sosok='+sosok+'&page='+str(i)+'">'+str(i)+'</a></td>'
    if page != lastpagev:

        if page > lastpagev -10:
            pages += '<td><a href="stockchart?sosok='+sosok+'&page='+str(lastpagev)+'">></td>'
        else:
            pages += '<td><a href="stockchart?sosok='+sosok+'&page='+str(page+10)+'">></td>'
        pages += '<td><a href="stockchart?sosok='+sosok+'&page=' + str(lastpagev) + '">>></td>'
    pages += '</tr></table>'
    return render(request,"pagingserver.html",{"page":pages})


def stockdetail(request):
    name = request.GET['name']
    sosok = request.GET['sosok']
    df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]
    code = str(df[df['회사명'] == name]['종목코드'].values[0])
    code = code.zfill(6)
    if sosok  == '0':
        sosok = 'KOSPI'
    else:
        sosok = 'KOSDAK'
    return render(request,"stockdetail.html",{"name":name,"code":code,'sosok':sosok})


def today(request):
    code = request.GET['code']
    url = 'https://finance.naver.com/item/main.nhn?code='+code
    print(url)
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
    hogatable = gethogatable(request,code)

    return render(request,"stocktodayserver.html",{"price":price,"priceupdown":priceupdown,"priceper":priceper,"yesterday":yesterday,"pricemax":pricemax,
                                                   "dill":dill,"pricesiga":pricesiga,"pricemin":pricemin,"updown":updown,"dillprice":dillprice,
                                                   "chart":chart,'maxcolor':maxcolor,'mincolor':mincolor,'sigacolor':sigacolor,
                                                   'color':color,'date':date,"hoga":hogatable})
hogatable = "";
def gethogatable(request,code):
    url = 'https://finance.naver.com/item/main.nhn?code=' + code
    print(url)
    site = rq.get(url)
    site2 = site.content.decode('euc-kr')
    soup = bs(site2, 'html.parser')
    hogamax = []


    for i in range(5, 10):
        hoga1 = int(''.join(
            soup.select('#tab_con2 > table .f_down td:nth-child(1)')[i].text.replace('\n', "").replace('\t', "").split(
                ',')))
        print(hoga1)
        hogamax.append(hoga1)
    for i in range(0, 5):
        hoga2 = int(''.join(
            soup.select('#tab_con2 > table .f_up td:nth-child(3)')[i].text.replace('\n', "").replace('\t', "").split(
                ',')))
        print(hoga2)
        hogamax.append(hoga2)
    print(hogamax)
    hogatable = '''<table class="hoga"><thead><tr><td>매도잔량</td><td>호가<td><td>매수잔량</td></tr><thead>
    <tfoot><tr><td></td><td></td><td></td></tr></tfoot><tbody>
    '''
    for i in range(5, 10):
        print(hogamax[i - 5])
        hoga1 = soup.select('#tab_con2 > table .f_down td:nth-child(1)')[i].text
        hoga2 = soup.select('#tab_con2 > table .f_down td:nth-child(2)')[i].text
        hogatable += '<tr class="f_down"><td><div class="grp"><div style="width:' + str(
            int((int(hogamax[i - 5]) / max(hogamax)) * 100)) + '%;">' + str(
            hoga1) + '</div></div></td><td>' + str(hoga2) + '</td><td></td></tr>'
    for i in range(0, 5):
        hoga1 = soup.select('#tab_con2 > table .f_up td:nth-child(2)')[i].text
        hoga2 = soup.select('#tab_con2 > table .f_up td:nth-child(3)')[i].text
        hogatable += '<tr class="f_up"><td></td><td>' + str(hoga1) + '</td><td><div class="grp"><div style="width:' + str(
            int((hogamax[i + 5] / max(hogamax)) * 100)) + '%;">' + str(hoga2) + '</div></td></tr>'
    hogatable += '</tbody></table>'
    return hogatable

def order(request):

    return render(request,"stockorder.html")