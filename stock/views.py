from django.shortcuts import render ,redirect
from stock import models
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from bs4 import BeautifulSoup as bs
import pandas as pd


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
    url = 'https://finance.naver.com/sise/sise_market_sum.nhn?&page='+str(key["page"])
    result = pd.read_html(url, encoding="euc-kr")[1]
    result = result.iloc[:,:-3].dropna().reset_index(drop=True)
    result['N'] = result['N'].astype(int)
    return result

def stockchart(request):
    return render(request,"stockchart.html")

def stockchartajax(request):
    page = request.GET['page']
    stockchart = getNaverStockData(page=1).to_html(index=False)
    print(stockchart)
    return render(request,"stockchartserver.html",{"stockchart":stockchart})