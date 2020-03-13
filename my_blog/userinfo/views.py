from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
# from .forms import UserLoginForm, UserRegisterForm
from django.http import HttpResponse
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from .models import UserInfo,get_default_avatar_url
from .forms import UserInfoForm,PhotoForm
from allauth.account.models import EmailAddress
from allauth.account.views import EmailView
from django.contrib.auth.hashers import check_password
from braces.views import LoginRequiredMixin
"""
思路：
注册模块：判断输入与数据库是否重复
登陆模块
"""
def user_signup_validate(request):
    """登陆/注册验证（validate）"""
    data = request.POST
    on_validate_type = data.get('type')
    #signup注册
    if on_validate_type == 'username':
        """输入的用户名在数据库已经存在，返回服务器拒绝请求"""
        if User.objects.filter(username__iexact=data.get('username')).exists():
            return HttpResponse('403')
    elif on_validate_type == 'email':
        if EmailAddress.objects.filter(email__iexact=data.get('email')).exists():
            return HttpResponse('403')
    #login
    elif on_validate_type == 'login':
        #输入的密码
        password = data.get('password')
        """filter过滤  get 匹配一个"""
        if User.objects.filter(username__iexact=data.get('login')).exists():
            user = User.objects.get(username__iexact=data.get('login'))
            if check_password(password, user.password):
                return HttpResponse('200')
            else:
                return HttpResponse('403')
        elif EmailAddress.objects.filter(email__iexact=data.get('login')).exists():
            user = EmailAddress.objects.get(email__iexact=data.get('login')).user
            if check_password(password, user.password):
                return HttpResponse('200')
            else:
                return HttpResponse('403')
        else:
            return HttpResponse('403')
    return HttpResponse('200')

class UserInfoView(LoginRequiredMixin, EmailView):
    """
    展示个人信息
    """
    success_url = reverse_lazy('userinfo:detail')
    login_url = "/accounts/login"
    def get_context_data(self, **kwargs):
        """添加或新建userinfo上下文"""
        context = super(UserInfoView, self).get_context_data(**kwargs)
        user_id = self.request.user.id
        try:
            """获取之前保存的头像"""
            userinfo = UserInfo.objects.get(user_id=user_id)
        except:
            """创建头像"""
            userinfo = UserInfo.objects.create(user_id=user_id)
            """使用系统头像"""
        if not userinfo.avatar:
            userinfo.avatar = get_default_avatar_url()
            userinfo.save()
        userinfo_form = UserInfoForm()
        data = {
            'userinfo': userinfo,
            'userinfo_form': userinfo_form,
        }
        context.update(data)
        return context

@login_required(login_url='/accounts/login')
def crop_upload_handler(request):
    """剪裁并上传头像"""
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            user_id = request.user.id
            form.save(user_id=user_id)
    return redirect('userinfo:detail')

# Create your views here.
# def user_login(request):
#     if request.method == 'POST':
#         user_login_form = UserLoginForm(data=request.POST)
#         if user_login_form.is_valid():
#             data = user_login_form.cleaned_data
#             user = authenticate(username=data['username'], password=data['password'])
#             if user:
#                 login(request, user)
#                 return redirect("article:article_list")
#             else:
#                 return HttpResponse("账号或密码输入有误!请重新输入:")
#         else:
#             return HttpResponse("账号或密码输入不合法")
#     elif request.method == 'GET':
#         user_login_form = UserLoginForm()
#         context = { 'form': user_login_form }
#         return render(request, 'userinfo/login.html', context)
#     else:
#         return HttpResponse("请使用GET或POST请求数据")
# def user_logout(request):
#     logout(request)
#     return redirect("article:article_list")
# def user_register(request):
#     if request.method == 'POST':
#         user_register_form = UserRegisterForm(data=request.POST)
#         if user_register_form.is_valid():
#             #先不保存到数据库
#             new_user = user_register_form.save(commit=False)
#             new_user.set_password(user_register_form.cleaned_data['password'])
#             new_user.save()
#             login(request, new_user)
#             return redirect("article:article_list")
#         else:
#             return HttpResponse("密码不一致！请重新输入！")
#     elif request.method == 'GET':
#         user_register_form = UserRegisterForm()
#         context = { 'form': user_register_form }
#         return render(request, 'userinfo/register.html', context)
#     else:
#         return HttpResponse("请使用GET或POST请求数据")
# @login_required(login_url='/userinfo/login/')
# def user_delete(request, id):
#     if request.method == 'POST':
#         user= User.objects.get(id=id)
#         if request.user == user:
#             logout(request)
#             user.delete()
#             return redirect("article:article_list")
#         else:
#             return HttpResponse("你没有删除操作的权限")
#     else:
#         return HttpResponse("仅接受post请求")
# @login_required(login_url='/userinfo/login/')
# def profile_edit(request, id):
#     user = User.objects.get(id=id)
#     # profile = Profile.objects.get(user_id=id)
#     if Profile.objects.filter(user_id=id).exists():
#         profile = Profile.objects.get(user_id=id)
#     else:
#         profile = Profile.objects.create(user=user)
#     if request.method == 'POST':
#         if request.user != user:
#             return HttpResponse("你没有权限修改此用户信息")
#         # 图片处理
#         # 上传的文件保存在 request.FILES 中，通过参数传递给表单类
#         profile_form = ProfileForm(request.POST, request.FILES)
#         if profile_form.is_valid():
#             profile_cd = profile_form.cleaned_data
#             profile.phone = profile_cd['phone']
#             profile.bio = profile_cd['bio']
#             # 如果request.FILES中存在键为avatar的元素，
#             # 则将其赋值给profile.avatar（注意保存的是图片地址）；否则不进行处理。
#             if 'avatar' in request.FILES:
#                 profile.avatar = profile_cd["avatar"]
#             profile.save()
#             return redirect("userinfo:edit", id=id)
#         else:
#             return HttpResponse("注册表单输入有误！请重新输入~")
#     elif request.method == 'GET':
#         profile_form = ProfileForm()
#         context = { 'profile_form': profile_form, 'profile': profile, 'user': user }
#         return render(request, 'userinfo/edit.html', context)
#     else:
#         return HttpResponse("请使用GET或POST请求数据")

