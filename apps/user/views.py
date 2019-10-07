from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from apps.user.models import User
import re
# Create your views here.

def register(request):
    '''显示注册界面'''
    return  render(request, 'register.html')

def register_handle(request):
    '''注册处理'''
    # 接收数据
    username = request.POST.get('user_name')
    password = request.POST.get('pwd')
    email = request.POST.get('email')
    print(email)
    allow = request.POST.get('allow')

    # 数据校验
    if not all([username, password, email]):
        # 数据不完整
        return render(request, 'register.html', {'errmsg': '数据不完整'})

    # 校验邮箱
    if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
        return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

    if allow != 'on':
        return render(request, 'register.html', {'errmsg' : '请同意协议'})

    # 校验用户名是否存在
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        # 用户名不存在
        user = None
    # 用户名存在
    if user:
        return render(request, 'register.html', {'errmsg': '用户名已存在'})
    # 进行业务处理，注册
    user = User.objects.create_user(username, email, password)
    user.is_active = 0
    user.save()

    # 返回应答
    return redirect(reverse('goods:index'))