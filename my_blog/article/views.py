from comment.models import Comment
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import ArticlePost
import markdown
from .forms import ArticlePostForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import ArticleColumn
from comment.forms import CommentForm
from django.contrib.auth.backends import ModelBackend
from allauth.account.auth_backends import AuthenticationBackend


def article_list(request):
    #从 url 中提取查询参数
    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')
    #初始化查询集
    article_list = ArticlePost.objects.all()
    #搜索查询集
    if search:
        article_list = article_list.filter(
            #匹配title和body有输入的选项，search是内容
            Q(title__icontains=search) |
            Q(body__icontains=search)
        )
    else:
        search = ''
    #栏目查询集
    if column is not None and column.isdigit():
        article_list = article_list.filter(column=column)
    #标签查询集
    #在tags字段中过滤name为tag的数据条目
    if tag and tag != 'None':
        article_list = article_list.filter(tags__name__in=[tag])
    #查询集排序
    if order == 'total_views':
        article_list = article_list.order_by('-total_views')
    paginator = Paginator(article_list, 3)
    # 需要传递给模板（templates）的对象
    page = request.GET.get('page')
    articles = paginator.get_page(page)
    context = { 'articles': articles,
                'order': order,
                'search':search,
                'column':column,
                'tag':tag,
     }
    return render(request, 'article/list.html', context)

# 文章详情

def article_detail(request, id):
    # 取出相应的文章
    article = ArticlePost.objects.get(id=id)
    #取出文章评论
    comments = Comment.objects.filter(article=id)
    #引入评论表单
    comment_form = CommentForm()
    #浏览量加1
    article.total_views += 1
    article.save(update_fields=['total_views'])
    # # 需要传递给模板的对象
    '''

    第一个参数是需要渲染的文章正文article.body
    第二个参数载入了常用的语法扩展，markdown.extensions.extra中包括了缩写、表格等扩展，
    markdown.extensions.codehilite则是后面要使用的代码高亮扩展。
    '''
    # article.body = markdown.markdown(article.body,
    #     extensions=[
    #     # 包含 缩写、表格等常用扩展
    #     'markdown.extensions.extra',
    #     # 语法高亮扩展
    #     'markdown.extensions.codehilite',
    #     #目录扩展
    #     'markdown.extensions.toc',
    #     ])
    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
        ]
    )
    '''
    先将Markdown类赋值给一个临时变量md，然后用convert()
    方法将正文渲染为html页面。通过md.toc将目录传递给模板。
    '''

    article.body = md.convert(article.body)
    # 传到前端

    context = { 'article': article,
                'toc': md.toc,
                'comments': comments,
                'comment_form': comment_form,
                }
    # 载入模板，并返回context对象
    return render(request, 'article/detail.html', context)

@login_required(login_url='/userinfo/login/')
def article_create(request):
    if request.method == "POST":
#POST的表单中包含了图片文件，所以要将request.FILES也一并绑定到表单类中，否则图片无法正确保存
        article_post_form = ArticlePostForm(request.POST, request.FILES)
        if article_post_form.is_valid():
            new_article = article_post_form.save(commit=False)
            new_article.author = User.objects.get(id=request.user.id)

            if request.POST['column'] != 'none':
                #根据表单提交的value值，关联对应的栏目
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            new_article.save()
            # 新增代码，保存 tags 的多对多关系
            article_post_form.save_m2m()
            return redirect("article:article_list")
        else:
            return HttpResponse("文章为空！")
    else:
        #增加栏目的上下文，以便模板使用
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        context = { 'article_post_form': article_post_form, 'columns': columns }
        return render(request, 'article/create.html', context)


"""
当视图函数接收到一个客户端的request请求时，首先根据request.method判断用户是要提交数据（POST）、还是要获取数据（GET）：

如果用户是提交数据，将POST给服务器的表单数据赋于article_post_form实例。

然后使用Django内置的方法.is_valid()判断提交的数据是否满足模型的要求。

如果满足要求，保存表单中的数据（但是commit=False暂时不提交到数据库，因为author还未指定），并指定author为id=1的管理员用户。
然后提交到数据库，并通过redirect返回文章列表。redirect可通过url地址的名字，反向解析到对应的url。

如果不满足要求，则返回一个字符串"表单内容有误，请重新填写。"，告诉用户出现了什么问题。

如果用户是获取数据，则返回一个空的表单类对象，提供给用户填写。

"""
@login_required(login_url='/userinfo/login/')
def article_delete(request,id):
    article = ArticlePost.objects.get(id=id)
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")
    else:
        article.delete()
        return redirect("article:article_list")

def article_safe_delete(request,id):
    if request.method == 'POST':
        article = ArticlePost.objects.get(id=id)
        article.delete()
        return redirect("article:article_list")
    else:
        return HttpResponse("仅允许POST请求")
#过滤未登录用户
@login_required(login_url='/userinfo/login/')
def article_update(request, id):
# 旧的整个对象的数据
    article = ArticlePost.objects.get(id=id)
#过滤非作者用户
    if request.user != article.author:
        return  HttpResponse("抱歉，你无权修改这篇文章。")
# 判断用户是否为 POST 提交表单数据
    if request.method == "POST":
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            article.title = request.POST['title']
            article.body = request.POST['body']
            #如果提交的POST的column数据不为空：
            if request.POST['column'] != 'none':
                ArticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column =None
            if request.FILES.get('avatar'):
                article.avatar = request.FILES.get('avatar')
            article.tags.set(*request.POST.get('tags').split(','), clear=True)
            article.save()
            return redirect("article:article_detail", id=id)
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    else:
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        context = {
            'article': article,
            'article_post_form': article_post_form,
            'columns': columns,
            'tags': ','.join([x for x in article.tags.names()]),
            }
        return render(request, 'article/update.html', context)


