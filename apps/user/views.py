from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from celery_tasks.tasks import send_register_active_email
from django.contrib.auth import authenticate, login, logout
from utils.mixin import LoginRequiredMixin
from django.views.generic import View
from django.http import HttpResponse
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer  # 加密
from itsdangerous import SignatureExpired
from apps.user.models import User
import apps.goods
import re
# Create your views here.

# def register(request):
#     '''显示注册界面'''
#     if request.method == 'GET':
#         # 显示注册页面
#         return render(request, 'register.html')
#     else:
#         # 注册处理
#         # 接收数据
#         username = request.POST.get('user_name')
#         password = request.POST.get('pwd')
#         email = request.POST.get('email')
#         print(email)
#         allow = request.POST.get('allow')
#
#         # 数据校验
#         if not all([username, password, email]):
#             # 数据不完整
#             return render(request, 'register.html', {'errmsg': '数据不完整'})
#
#         # 校验邮箱
#         if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
#             return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})
#
#         if allow != 'on':
#             return render(request, 'register.html', {'errmsg': '请同意协议'})
#
#         # 校验用户名是否存在
#         try:
#             user = User.objects.get(username=username)
#         except User.DoesNotExist:
#             # 用户名不存在
#             user = None
#         # 用户名存在
#         if user:
#             return render(request, 'register.html', {'errmsg': '用户名已存在'})
#         # 进行业务处理，注册
#         user = User.objects.create_user(username, email, password)
#         user.is_active = 0
#         user.save()
#
#         # 返回应答
#         return redirect(reverse('goods:index'))

# def register_handle(request):
#     ''''''
#     # 接收数据
#     username = request.POST.get('user_name')
#     password = request.POST.get('pwd')
#     email = request.POST.get('email')
#     print(email)
#     allow = request.POST.get('allow')
#
#     # 数据校验
#     if not all([username, password, email]):
#         # 数据不完整
#         return render(request, 'register.html', {'errmsg': '数据不完整'})
#
#     # 校验邮箱
#     if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
#         return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})
#
#     if allow != 'on':
#         return render(request, 'register.html', {'errmsg' : '请同意协议'})
#
#     # 校验用户名是否存在
#     try:
#         user = User.objects.get(username=username)
#     except User.DoesNotExist:
#         # 用户名不存在
#         user = None
#     # 用户名存在
#     if user:
#         return render(request, 'register.html', {'errmsg': '用户名已存在'})
#     # 进行业务处理，注册
#     user = User.objects.create_user(username, email, password)
#     user.is_active = 0
#     user.save()
#
#     # 返回应答
#     return redirect(reverse('goods:index'))

class RegisterView(View):
    '''注册'''
    def get(self, request):
        # 显示注册页面
        return render(request, 'register.html')

    def post(self, request):
        # 注册处理
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
            return render(request, 'register.html', {'errmsg': '请同意协议'})

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

        # 发送激活邮件，包含激活链接：127.0.0.1:8000/user/active/1
        # 激活链接包含用户身份信息,身份信息加密处理

        # 加密用户信息，生成激活token
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        token = serializer.dumps(info)
        token = token.decode()

        # 发邮件
        # subject = '天天生鲜欢迎信息'
        # message = ''
        # html_message = '<h1>%s, 欢迎您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>'%(username, token, token)
        # sender = settings.EMAIL_FROM
        # receiver = [email]
        # send_mail(subject, message, sender, receiver, html_message=html_message)

        # 返回应答
        send_register_active_email.delay(email, username, token)

        return redirect(reverse('goods:index'))

class ActiveView(View):
    '''用户激活'''
    def get(self, request, token):
        '''激活用户'''
        # 进行解密， 获取用户信息
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            # 获取代激活用户id
            user_id = info['confirm']

            # 根据id获取用户信息
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            # 跳转登录页面
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            # 激活链接失效
            return HttpResponse('激活链接失效')

class LoginView(View):
    '''登录'''
    def get(self, request):
        '''显示登录页面'''
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        return render(request, 'login.html', {'username': username, 'checked': checked})

    def post(self, request):
        '''登录校验'''
        # 接收数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')

        # 校验数据
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '数据不完整'})

        # 业务处理：登录校验
        user = authenticate(username=username, password=password)
        if user is not None:
            # 用户名密码正确
            if user.is_active:
                # 用户已激活
                # 记录用户的登录状态
                login(request, user)
                # 获取要跳转的地址
                # 默认跳转首页
                next_url = request.GET.get('next', reverse('goods:index'))
                # 跳转到next_url
                response =  redirect(next_url)

                # 判断是否需要记住用户名
                remember = request.POST.get('member')

                if remember == 'on':
                    # 记住用户名
                    response.set_cookie('username', username, max_age=7 * 24 * 3600)
                else:
                    response.delete_cookie('username')

                # 返回response
                return response
            else:
                return render(request, 'login.html', {'errmsg': '账户未激活'})
        else:
            return render(request, 'login.html', {'errmsg': '用户名密码错误'})

class LogoutView(View):
    '''退出登录'''
    def get(self, request):
        # 清楚用户session信息
        logout(request)
        # 跳转首页
        return render(request, 'index.html')


class UserInfoView(LoginRequiredMixin, View):
    '''用户中心页面'''
    def get(self, request):
        '''显示'''
        return render(request, 'user_center_info.html', {'page': 'user'})

class UserOrderView(LoginRequiredMixin, View):
    '''用户订单页'''
    def get(self, request):
        '''显示'''
        return render(request, 'user_center_order.html', {'page': 'order'})

class AddressView(LoginRequiredMixin, View):
    '''用户中心地址信息'''
    def get(self, request):
        '''显示'''
        return render(request, 'user_center_site.html', {'page': 'address'})



