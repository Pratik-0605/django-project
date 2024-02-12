from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from ecartapp.models import product,Cartt,Order
from django.db.models import Q
import random
import razorpay
from django.core.mail import send_mail

# Create your views here.
def home(request):
    userid=request.user.id
    #print("id of logged in user:",userid)
    #print("Result:",request.user.is_authenticated)
    context={}
    p=product.objects.filter(is_active=True)
    context['products']=p
    print(p)
    return render(request,"index.html",context)

def pdetails(request,pid):
    context={}
    p=product.objects.filter(id=pid)
    context['products']=p
    return render(request,"pdetails.html",context)

def viewcart(request):
    c=Cartt.objects.filter(uid=request.user.id)
    print(c)
    #print(c[0].pid)
    #print(c[0].uid)
    #print(c[0].pid.name)
    context={}
    context['data']=c
    s=0
    for x in c:
        s=s+x.pid.price * x.qty
    print(s)
    context['total']=s
    np=len(c)
    context['items']=np
    return render(request,"viewcart.html",context)

def register(request):
    if request.method=="POST":
        uname=request.POST['uname']
        upass=request.POST['upass']
        ucpass=request.POST['ucpass']
        context={}
        if uname=="" or upass=="" or ucpass=="":
            context['errmsg']="Fields cannot be empty"
            return render(request,"register.html",context)
        elif upass!=ucpass:
            context['errmsg']="Passwords did not match"
            return render(request,"register.html",context)
        else:
            try:
                u=User.objects.create(password=upass,username=uname,email=uname)
                u.set_password(upass)
                u.save()
                context['success']="User registered successfully"
                return render(request,"register.html",context)
            except Exception:
                context['errmsg']="Username already exists! Try login."
                return render(request,"register.html",context)

    else:
        return render(request,"register.html")
    
def ulogin(request):
    if request.method=="POST":
        uname=request.POST['uname']
        upass=request.POST['upass']
        context={}
        if uname=="" or upass=="":
            context['errmsg']="Fields cannot be empty"
            return render(request,"login.html",context)
            #print(uname)
            #print(upass)
            #return HttpResponse("Data fetched")
        else:
            u=authenticate(username=uname,password=upass)
            #print(u)
            if u is not None:
                login(request,u)
                return redirect('/home')
            else:
                context['errmsg']="Invalid Username/password"
                return render(request,"login.html",context)
    else:
        return render(request,"login.html")

def ulogout(request):
    logout(request)
    return redirect('/home')

def cartfilter(request,cv):
    q1=Q(is_active=True)
    q2=Q(cart=cv)
    p=product.objects.filter(q1 & q2)
    print(p)
    context={}
    context['products']=p
    return render(request,"index.html",context)

def sort(request,sv):
    if sv=='0':
        col='price'
    else:
        col='-price'
    p=product.objects.filter(is_active=True).order_by(col)
    context={}
    context['products']=p
    return render(request,"index.html",context)

def range(request):
    min=request.GET['min']
    max=request.GET['max']
    q1=Q(price__gte=min)
    q2=Q(price__lte=max)
    q3=Q(is_active=True)
    p=product.objects.filter(q1 & q2 & q3)
    context={}
    context['products']=p
    return render(request,"index.html",context)

def addtocartt(request,pid):
    if request.user.is_authenticated:
        userid=request.user.id
        u=User.objects.filter(id=userid)
        print(u)
        p=product.objects.filter(id=pid)
        print(p)
        q1=Q(uid=u[0])
        q2=Q(pid=p[0])
        c=Cartt.objects.filter(q1 & q2)
        print(c)
        context={}
        n=len(c)
        if n==1:
            context['errmsg']="Product already exists in cart"
            context['products']=p
            return render(request,'pdetails.html',context)
        else:
            c=Cartt.objects.create(uid=u[0],pid=p[0])
            c.save()
            context={}
            context['success']="Product added to cart!!"
            context['products']=p
            return render(request,"pdetails.html",context)
    else:
        return redirect('/login')
 
def remove(request,cid):
    c=Cartt.objects.filter(id=cid)
    c.delete()
    return redirect('/viewcart')

def updateqty(request,qv,cid):
    c=Cartt.objects.filter(id=cid)
    if qv=='1':
        t=c[0].qty+1
        c.update(qty=t)
    else:
        t=c[0].qty-1
        c.update(qty=t)
    return redirect('/viewcart')

def placeorder(request):
    userid=request.user.id
    c=Cartt.objects.filter(uid=userid)
    oid=random.randrange(1000,9999)
    for x in c:
        o=Order.objects.create(order_id=oid,pid=x.pid,uid=x.uid,qty=x.qty)
        o.save()
        x.delete()
    orders=Order.objects.filter(uid=request.user.id)
    context={}
    context['data']=orders
    s=0
    for x in orders:
        s=s+x.pid.price * x.qty
    context['total']=s
    np=len(orders)
    context['items']=np
    return render(request,'placeorder.html',context)

def makepayment(request):
    orders=Order.objects.filter(uid=request.user.id)
    s=0
    np=len(orders)
    for x in orders:
        s=s+x.pid.price * x.qty
        oid=x.order_id
    
    client = razorpay.Client(auth=("rzp_test_Wn3mlocL1inSV0", "I0lldLB5jb0KL1GDaMgfCGP8"))

    data = { "amount":(s*100), "currency": "INR", "receipt":oid }
    payment = client.order.create(data=data)
    context={}
    context['data']=payment
    uemail=request.user.username
    print(uemail)
    context['uemail']=uemail
    return render(request,'pay.html',context)

def sendusermail(request):
    send_mail(
    "Ecart-Order Placed Successfully",
    "Order Completed!! Thanks for ordering.",
    "anonymous988t@gmail.com",
    ["anonymous0562001@gmail.com"],
    fail_silently=False,
    )
    return HttpResponse("Email Sent!!")