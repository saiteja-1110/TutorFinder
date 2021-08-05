from django.http.response import HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth.models import User,auth
from django.contrib.auth.forms import UserCreationForm
from django.forms import inlineformset_factory
from .models import MyUser,Tutor,Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday,Orders,Review
from django.contrib import messages
from django.shortcuts import render,get_object_or_404
from django.http import Http404
from django.contrib.auth import authenticate,login,logout
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password,check_password
from django.db.models import Q
from django.urls import reverse
from django.conf import settings
from django.views.decorators.cache import cache_control
import datetime
import time
import calendar
import itertools
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from . import Checksum

MERCHANT_KEY=''

def logoutView(request):
    auth.logout(request)
    return redirect("home")

def tutorView(request):
    print(request.user.is_authenticated)
    if request.user.is_authenticated:
        l=[]
        day=[]
        o=Orders.objects.filter(tutor_name=request.user.username).order_by('date')
        today = datetime.date.today()
        for i in range(0,7):
                Previous_Date = today + datetime.timedelta(days=i)
                x=Previous_Date.__str__()
                year, month, d = (int(i) for i in x.split('-'))   
                born = datetime.date(year, month, d)
                l.append(x)
                day.append(born.strftime("%A"))
        print(l)
        user=MyUser.objects.get(username=request.user.username)
        t=Tutor.objects.get(tutor=user)
        print(t)
        if(o):
            s=""
        else:
            s="No Bookings yet!"
        context={"t":t,"book":o,"dates":l,"mesg":s}
        return render(request,'tutor.html',context)
    else:
        return redirect('login')

@login_required(login_url='login')
def reviewView(request,my_id):
    if request.user.is_authenticated:
        try:
            tut=Tutor.objects.get(id=my_id)
        except tut.DoesNotExist:
            raise Http404
        if request.method== 'POST':
                context={}
                stars=request.POST['rate']
                content=request.POST.get('content')
                if(stars=="1"):
                    title="Bad"
                if(stars=="2"):
                    title="Not Bad"
                if(stars=="3"):
                    title="Good"
                if(stars=="4"):
                    title="Very Good"
                if(stars=="5"):
                    title="Excellent"
                try:
                    if(Review.objects.get(tut=tut,user=request.user)):
                        review=Review.objects.get(tut=tut,user=request.user)
                        review.title=title
                        review.content=content
                        review.stars=stars
                        review.save()
                        mesg="Changes Saved"
                except:
                    review=Review(tut=tut,user=request.user,title=title,content=content,stars=stars)
                    review.save()
                    mesg="Submitted review successfully"
                content=review.content
                title=review.title
                stars=int(review.stars)
                starslist=[0,0,0,0,0]
                for i in range(0,stars):
                        starslist[i]=1
                context={'tut':tut,'content':content,'title':title,'mesg':mesg,'stars':stars,"starslist":starslist}
                return render(request,'review.html',context)
        else:
            context={}
            content=""
            title=""
            stars=0
            starslist=[0,0,0,0,0]
            try:
                if(Review.objects.get(tut=tut,user=request.user)):
                    review=Review.objects.get(tut=tut,user=request.user)
                    content=review.content
                    title=review.title
                    stars=int(review.stars)
                    for i in range(0,stars):
                        starslist[i]=1
                    context={'tut':tut,'content':content,'title':title,'stars': stars,"starslist":starslist}
                return render(request,'review.html',context)
            except:
                context={'tut':tut,'content':content,'title':title,'stars':stars,"starslist":starslist}
                return render(request,'review.html',context)
    else:
        return redirect('login')

def orderView(request):
    print(request.user.username)
    o=Orders.objects.filter(stud_name=request.user.username)
    lis={"orders":o}
    return render(request,'MyOrders.html',lis)

@login_required(login_url='login')
def demoView(request,my_id):
    try:
        tr=Tutor.objects.get(id=my_id)
        print(tr)
    except tr.DoesNotExist:
        raise Http404
    lis={"t":tr}
    return render(request,'demoVideo.html',lis)


def displayView(request):
        data=Tutor.objects.all()
        print(data)
        lis={}
        if request.method=='POST':
            clas=request.POST.getlist('teach')
            maxfee=request.POST['tfee']
            sub=request.POST.getlist('tsub')
            print(clas,maxfee,sub)
            data=data.filter(Q(mode="offline") | Q(mode="both"))
            if(maxfee!=""):
                data=data.filter(Q(fees__lte = maxfee))
            if(len(sub)!=0):
                query = Q(subjects__contains=sub[0])
                for i in range(1,len(sub)):
                    query.add(Q(subjects__contains=sub[i]), Q.OR)
                data=data.filter(query)
            if(len(clas)!=0):
                query = Q(teach__contains=clas[0])
                for i in range(1,len(clas)):
                    query.add(Q(teach__contains=clas[i]), Q.OR)
                data=data.filter(query)
            print(data)
        s=""
        if(data):
            s=""
        else:
            s="No Results Found!"
        lis={"tutor":data,"mesg":s}
        return render(request,'tutordisplay.html',lis)


def bookView(request,my_id):
        if request.method=='POST':
            print(request.POST)
            try:
                tr=Tutor.objects.get(id=my_id)
                print(tr)
            except tr.DoesNotExist:
                raise Http404
            l=[]
            day=[]
            today = datetime.date.today()
            for i in range(0,7):
                Previous_Date = today + datetime.timedelta(days=i+1)
                x=Previous_Date.__str__()
                year, month, d = (int(i) for i in x.split('-'))   
                born = datetime.date(year, month, d)
                l.append(x)
                day.append(born.strftime("%A"))
            z=zip(l,day)
            print(z)
            day=request.POST.get('day')
            s=request.POST['time']
            s1=request.POST['time1']
            date=request.POST['date']
            print(date)
            for i,j in z:
                if(j==date):
                    date1=i
            print(date1)
            order=Orders(stud_name=request.user.username,stud_email=request.user.email,tutor_name=tr.tutor.username,tutor_email=tr.tutor.email,stud_phn=request.user.phn_num,tutor_phn=tr.tutor.phn_num,fee=tr.fees,day=day,time=s1,time1=s,date=date1)
            order.save()
            print(s)
            print("Successful")
            id=order.id
            print(id)
            param_dict = {

                    'MID': '',
                    'ORDER_ID': str(id),
                    'TXN_AMOUNT': str(tr.fees),
                    'CUST_ID': request.user.username,
                    'INDUSTRY_TYPE_ID': 'Retail',
                    'WEBSITE': 'WEBSTAGING',
                    'CHANNEL_ID': 'WEB',
                    'CALLBACK_URL':'http://localhost:8000/handlerequest/',

            }
            if(order.status!="Success"):
                param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
                return render(request, 'paytm.html', {'param_dict': param_dict})
            else:
                return redirect('mode.html')
        else:
            try:
                tr=Tutor.objects.get(id=my_id)
                print(tr)
            except tr.DoesNotExist:
                raise Http404
            mon=Monday.objects.get(monday=tr)
            tues=Tuesday.objects.get(tuesday=tr)
            wed=Wednesday.objects.get(wednesday=tr)
            thur=Thursday.objects.get(thursday=tr)
            fri=Friday.objects.get(friday=tr)
            sat=Saturday.objects.get(saturday=tr)
            sun=Sunday.objects.get(sunday=tr)
            today = datetime.date.today()
            g=today.weekday()
            day=calendar.day_name[g]
            t = time.localtime()
            ct = time.strftime("%H:%M:%S", t)
            p = (today - datetime.timedelta(days=1)).weekday()
            d=calendar.day_name[p]
            print(tr.slots)
            x1=tr.slots[1:len(tr.slots)-1]
            l1=list(x1.split(', '))
            print(l1)
            for i in l1:
                i=i[1:len(i)-1]
                if(d=="Monday"):
                    setattr(mon,i,"1")
                if(d=="Tuesday"):
                    setattr(tues,i,"1")
                if(d=="Wednesday"):
                    setattr(wed,i,"1")
                if(d=="Thursday"):
                    setattr(thur,i,"1")
                if(d=="Friday"):
                    setattr(fri,i,"1")
                if(d=="Saturday"):
                    setattr(sat,i,"1")
                if(d=="Sunday"):
                    setattr(sun,i,"1")
            mon.save()
            tues.save()
            wed.save()
            thur.save()
            fri.save()
            sat.save()
            sun.save()
            l=[]
            day=[]
            for i in range(0,7):
                Previous_Date = today + datetime.timedelta(days=i+1)
                x=Previous_Date.__str__()
                year, month, d = (int(i) for i in x.split('-'))   
                born = datetime.date(year, month, d)
                l.append(x)
                day.append(born.strftime("%A"))
            z=zip(l,day)
            print(z)
            con={"wd":z,"mon":mon,"tues":tues,"wed":wed,"thur":thur,"fri":fri,"sat":sat,"sun":sun,"tr":tr}
            return render(request,'book.html', con)

@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)

def handlerequest(request):
        form = request.POST
        response_dict = {}
        for i in form.keys():
            response_dict[i] = form[i]
            if i == 'CHECKSUMHASH':
                checksum = form[i]

        verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
        if verify:
            oid=response_dict["ORDERID"]
            if response_dict['RESPCODE'] == '01':
                print('order successful')
                o=Orders.objects.get(id=oid)
                user=MyUser.objects.get(username=o.tutor_name)
                t=Tutor.objects.get(tutor=user)
                o.status="Success"
                o.save()
                send_mail(
                'Session booked',
                'Your session has been booked by '+ o.stud_name + ' at ' + o.time1 + ' on ' + o.date
                +'\n' + 'Student contact details :\n' + 'Email : '+ o.stud_email + '\nPhone Number : ' + o.stud_phn
                +'\n',
                settings.EMAIL_HOST_USER,
                [o.tutor_email],
                fail_silently=False,
                )
                send_mail(
                     'Session booked',
                     'Your session has been booked for '+ o.tutor_name + ' at ' + o.time1 + ' on ' + o.date + '\nPhone Number : '+ o.tutor_phn + '\n meeting link : ' + t.meeting,
                      settings.EMAIL_HOST_USER,
                     [o.stud_email],
                     fail_silently=False,
                )
                print(o.tutor_name)
                user1=MyUser.objects.get(username=o.tutor_name)
                user2=MyUser.objects.get(username=o.stud_name)
                print(user2)
                try:
                    tr=Tutor.objects.get(tutor=user1)
                    print(tr)
                except tr.DoesNotExist:
                    raise Http404
                print("a")
                print(tr)
                mon=Monday.objects.get(monday=tr)
                tues=Tuesday.objects.get(tuesday=tr)
                wed=Wednesday.objects.get(wednesday=tr)
                thur=Thursday.objects.get(thursday=tr)
                fri=Friday.objects.get(friday=tr)
                sat=Saturday.objects.get(saturday=tr)
                sun=Sunday.objects.get(sunday=tr)
                s=o.time
                x= user2.username + "," + user2.email + "," + user2.phn_num
                if(o.day=="Monday"):
                    print("a")
                    setattr(mon,s,x)
                    mon.save()
                if(o.day=="Tuesday"):
                    setattr(tues,s,x)
                    tues.save()
                if(o.day=="Wednesday"):
                    setattr(wed,s,x)
                    wed.save()
                if(o.day=="Thursday"):
                    setattr(thur,s,x)
                    thur.save()
                if(o.day=="Friday"):
                    setattr(fri,s,x)
                    fri.save()
                if(o.day=="Saturday"):
                    setattr(sat,s,x)
                    sat.save()
                if(o.day=="Sunday"):
                    setattr(sun,s,x)
                    sun.save()

            else:
                print('order was not successful because' + response_dict['RESPMSG'])
                o=Orders.objects.get(id=oid)
                o.status="Failure"
                o.save()
                print(o.time)
        # print(response_dict)
        return render(request, 'paymentstatus.html', {'response': response_dict})

def onlinedisView(request):
        data=Tutor.objects.all()
        if request.method=='POST':
            clas=request.POST.getlist('teach')
            maxfee=request.POST['tfee']
            sub=request.POST.getlist('tsub')
            print(clas,maxfee,sub)
            data=data.filter(Q(mode="online") | Q(mode="both"))
            if(len(sub)!=0):
                query = Q(subjects__contains=sub[0])
                for i in range(1,len(sub)):
                    query.add(Q(subjects__contains=sub[i]), Q.OR)
                data=data.filter(query)
            if(len(clas)!=0):
                query = Q(teach__contains=clas[0])
                for i in range(1,len(clas)):
                    query.add(Q(teach__contains=clas[i]), Q.OR)
                data=data.filter(query)
            if(maxfee!=""):
                data=data.filter(fees__range = (100,maxfee))
        s=""
        if(data):
            s=""
        else:
            s="No Results Found!"
        lis={"tutor":data,"mesg":s}
        return render(request,'display(online).html',lis)

@login_required(login_url='login')
def adminView(request):
    print(request.user.is_authenticated)
    if request.user.is_authenticated:
        t=Tutor.objects.all()
        context={"t":t}
        return render(request,'admin.html',context)
    else:
        return redirect('login')

@login_required(login_url='login')
def fulldetailsView(request,my_id):
    if request.user.is_authenticated:
        context={}
        t= Tutor.objects.get(id=my_id)
        if request.method == 'POST':
            user=MyUser.objects.get(username=t.tutor.username)
            user.delete()
            return redirect('admin1')
        context={"t":t}
        return render(request,'fulldetails.html',context)
    else:
        return redirect('login')

@login_required(login_url='login')
def verify(request,my_id):
    if request.user.is_authenticated:
        context={}
        t= Tutor.objects.get(id=my_id)
        print(t.is_verified)
        t.is_verified=True
        t.save()
        context={"t":t}
        return render(request,'fulldetails.html',context)
    else:
        return redirect('login')

def modeView(request):
    if request.user.is_authenticated:
        return render(request,'mode.html')
    else:
        return redirect('login')

def modeView1(request):
    response = redirect('/mode/')
    return response

@login_required(login_url='login')
def tutorprofileView(request):
    if request.user.is_authenticated:
        context={}
        if request.method=='POST':
                username=request.POST['username']
                email=request.POST['email']
                phonenum=request.POST['phone']
                locality=request.POST['loc']
                high_qual=request.POST['qua']
                fees=request.POST['fee']
                dist=request.POST.get('dist')
                sub=request.POST.getlist('teach')
                t_can=request.POST.getlist('can_t')
                slot=request.POST.getlist('slot')
                mode=request.POST['mode']
                user=MyUser.objects.get(username=username)
                try:
                    u=MyUser.objects.get(email=email)
                    if(user.username!=u.username):
                        context['mesg']="Email already exists try with another email"
                        return render(request,'edit_profile(tut).html',context)
                except:
                    pass
                s="Changes saved"
                user.email = email
                user.phn_num=phonenum
                user.locality=locality
                user.save()
                t1=Tutor.objects.get(tutor=user)
                mon=Monday.objects.get(monday=t1)
                tues=Tuesday.objects.get(tuesday=t1)
                wed=Wednesday.objects.get(wednesday=t1)
                thur=Thursday.objects.get(thursday=t1)
                fri=Friday.objects.get(friday=t1)
                sat=Saturday.objects.get(saturday=t1)
                sun=Sunday.objects.get(sunday=t1)
                print(t1.slots)
                x=t1.slots[1:len(t1.slots)-1]
                l=list(x.split(', '))
                print(l)
                for i in l:
                    i=i[1:len(i)-1]
                    print(i)
                    setattr(mon,i,"0")
                    setattr(tues,i,"0")
                    setattr(wed,i,"0")
                    setattr(thur,i,"0")
                    setattr(fri,i,"0")
                    setattr(sat,i,"0")
                    setattr(sun,i,"0")
                mon.save()
                tues.save()
                wed.save()
                thur.save()
                fri.save()
                sat.save()
                sun.save()
                t1.tutor=user
                t1.Highest_Qual=high_qual
                t1.fees=fees
                t1.travel=dist
                t1.subjects=sub
                t1.mode=mode
                t1.teach=t_can
                t1.slots=slot
                t1.save()
                for i in slot:
                    print(i)
                    setattr(mon,i,"1")
                    setattr(tues,i,"1")
                    setattr(wed,i,"1")
                    setattr(thur,i,"1")
                    setattr(fri,i,"1")
                    setattr(sat,i,"1")
                    setattr(sun,i,"1")
                mon.save()
                tues.save()
                wed.save()
                thur.save()
                fri.save()
                sat.save()
                sun.save()
                context={'tut':t1,'mesg':s}
                return render(request,'edit_profile(tut).html',context)
        else:
            user=MyUser.objects.get(username=request.user.username)
            t=Tutor.objects.get(tutor=user)
            context={'tut':t}
            return render(request,'edit_profile(tut).html',context)
        return render(request,'edit_profile(tut).html',context)
    else:
        return redirect('login')

@login_required(login_url='login')
def profileView(request):
    if request.user.is_authenticated:
        context={}
        if request.method=='POST':
                username=request.POST['username']
                email=request.POST['email']
                phonenum=request.POST['phone']
                locality=request.POST['loc']
                user=MyUser.objects.get(username=username)
                try:
                    u=MyUser.objects.get(email=email)
                    if(user.username!=u.username):
                        context['mesg']="Email already exists try with another email"
                        return render(request,'edit_profile.html',context)
                except:
                    pass
                context['mesg']="Changes saved"
                user.email = email
                user.phn_num=phonenum
                user.locality=locality
                user.save()
                return render(request,'edit_profile.html',context)
        return render(request,'edit_profile.html',context)
    else:
        return redirect('login')
def about(request):
    return render(request,'about.html')
def contact(request):
    context={}
    if request.method == 'POST':
        name=request.POST['customerName']
        email=request.POST['customerEmail']
        phonenumber=request.POST['customerPhone']
        note=request.POST['customerNote']
        print(name,email,phonenumber,note)
        subject = 'abc'
        message = name + "\n" +note
        email_from = email
        recipient_list = ["anvithareddyvangala30@gmail.com", ]
        send_mail(subject, message, email_from, recipient_list )
        mesg="Received Your Email"
        context={"mesg":mesg}
    return render(request,'contact.html',context)
def indexView(request):
    if request.user.is_authenticated:
        if request.user.is_tutor:
            return redirect('tutor')
        if request.user.is_student:
            return redirect('mode')
        if request.user.is_staff:
            return redirect('admin1')
    return render(request,'index.html')

def loginView(request):
    context={}
    mesg=""
    if request.method =="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        try:
            user=MyUser.objects.get(username=username)
            print(user)
        except:
            user=False
            print(user)
        if user :
            flag=check_password(password,user.password)
            print(flag)
            if flag :
                login(request,user)
                if request.user.is_tutor:
                    return redirect('tutor')
                elif request.user.is_superuser == True:
                    return redirect('http://127.0.0.1:8000/admin')
                elif request.user.is_staff == True:
                    return redirect('admin1')
                else:
                    print(user)
                    return redirect('mode')
            else:
                mesg="Password is incorrect"
                context={"mesg":mesg}
                return render(request,'registration/login.html',context)
        else:
            mesg="Username doesn't exist"
            context={"mesg":mesg}
            return render(request,'registration/login.html',context)
    return render(request,'registration/login.html',context)

def registerView(request):
        if(request.POST.get('submit')=='psignup'):
            username=request.POST['sname']
            email=request.POST['smail']
            password1=request.POST['spsw1']
            password2=request.POST['spsw2']
            phone=request.POST['sphone']
            loc=request.POST['locality']
            print("a")
            print(username,email,password1,phone)
            if(password1==password2):
                if(MyUser.objects.filter(username=username).exists()):
                    messages.info(request,"username already exists")
                elif(MyUser.objects.filter(email=email).exists()):
                    messages.info(request,'Email already exists')
                    return redirect('register')
                else:
                    messages.info(request,"create user")
                    user=MyUser(username=username,email=email,password=password1,phn_num=phone,locality=loc,is_tutor=False,is_student=True)
                    user.password=make_password(user.password)
                    print(user.password)
                    user.save()
            else:
                messages.info(request,'Passwords not matching')
                return redirect('register')
        elif(request.POST.get('submit')=='tsignup'):
            print("a")
            username=request.POST['tname']
            email=request.POST['tmail']
            password1=request.POST['tpsw1']
            password2=request.POST['tpsw2']
            gender=request.POST.get('tgen')
            high_qua=request.POST['thq']
            phone=request.POST['tphn']
            t_can=request.POST.getlist('teach')
            sub=request.POST.getlist('tsub')
            dist=request.POST.get('dist')
            mode=request.POST['mode']
            locality=request.POST['locality']
            state=request.POST['state']
            fee=request.POST['tfee']
            slot=request.POST.getlist('slot')
            mapurl=request.POST['url']
            exp=request.POST.get('exp')
            video=request.POST.get('video')
            meeting=request.POST['meet']
            print(slot)
            print(username,email,password1,phone,t_can,mode,dist,locality,state,fee)
            if(password1==password2):
                if(MyUser.objects.filter(username=username).exists()):
                    messages.info(request,"username already exists")
                elif(MyUser.objects.filter(email=email).exists()):
                    messages.info(request,'Email already exists')
                    return redirect('register')
                else:
                    messages.info(request,"create user")
                    user=MyUser(username=username,email=email,password=password1,phn_num=phone,locality=locality,is_tutor=True,is_student=False)
                    user.password=make_password(user.password)
                    print(user.password)
                    user.save()
                    tutor=Tutor(tutor=user,gender=gender,Highest_Qual=high_qua,mode=mode,teach=t_can,subjects=sub,travel=dist,state=state,fees=fee,slots=slot,mapurl=mapurl,experience=exp,video=video,meeting=meeting)
                    tutor.save()
                    monday=Monday(monday=tutor)
                    tuesday=Tuesday(tuesday=tutor)
                    wednesday=Wednesday(wednesday=tutor)
                    thursday=Thursday(thursday=tutor)
                    friday=Friday(friday=tutor)
                    saturday=Saturday(saturday=tutor)
                    sunday=Sunday(sunday=tutor)
                    print(tutor.slots)
                    for i in slot:
                        setattr(monday,i,"1")
                        setattr(tuesday,i,"1")
                        setattr(wednesday,i,"1")
                        setattr(thursday,i,"1")
                        setattr(friday,i,"1")
                        setattr(saturday,i,"1")
                        setattr(sunday,i,"1")
                    monday.save()
                    tuesday.save()
                    wednesday.save()
                    thursday.save()
                    friday.save()
                    saturday.save()
                    sunday.save()
            else:
                messages.info(request,'Passwords not matching')
                return redirect('register')
        return render(request,'registration/register_tutor.html')