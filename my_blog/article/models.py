from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from taggit.managers import TaggableManager
from PIL import Image
#Processed Image Field:图像处理领域
from imagekit.models import ProcessedImageField
#ResizeToFit:调整以适应
from imagekit.processors import ResizeToFit
from ckeditor.fields import RichTextField

class ArticleColumn(models.Model):
    """
    栏目的 Model
    """
    title = models.CharField(max_length=100, blank=True)
    #创建事件
    created = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.title




class ArticlePost(models.Model):
    """
    文章作者。参数 on_delete 用于指定数据删除的方式，避免两个关联表的数据不一致。
    使用 ForeignKey定义一个关系。这将告诉 Django，每个（或多个） ArticlePost 对象
    都关联到一个 User 对象。Django本身具有一个简单完整的账号系统（User），足以满
    足一般网站的账号申请、建立、权限、群组等基本功能。
    用户=作者，两者关联起来，括号里面表示是“一”

    """
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # 文章标题。models.CharField 为字符串字段，用于保存较短的字符串，比如标题
    title = models.CharField(max_length=100)
    # 文章正文。保存大量文本使用 TextField
    body = RichTextField()
    # 文章创建时间。参数 default=timezone.now 指定其在创建数据时将默认写入当前的时间
    created = models.DateTimeField(default=timezone.now)
    # 文章更新时间。参数 auto_now=True 指定每次数据更新时自动写入当前时间
    updated = models.DateTimeField(auto_now=True)
    #浏览量：存储正整数的字段
    total_views = models.PositiveIntegerField(default=0)
    #文章标签
    tags = TaggableManager(blank=True)
    # 文章标题图,标题图会上传到media/article/20190226这个目录中
    avatar = models.ImageField(upload_to='article/%Y%m%d/', blank=True)
    # 保存时处理图片,处理图片的代码
    def save(self, *args, **kwargs):
        #调用父函数的子函数（save函数）的功能
        article = super(ArticlePost, self).save(*args, **kwargs)
        #固定宽度缩放图片大小.把self.avatar筛掉没有标题图的文章,忽略浏览量保存的操作，免得每次用户进入文章详情页面都要处理标题图
        if self.avatar and not kwargs.get('update_fields'):
            image = Image.open(self.avatar)
            (x, y) = image.size
            new_x = 400
            new_y = int(new_x * (y / x))
            #Image.ANTIALIAS表示缩放采用平滑滤波
            resized_image = image.resize((new_x, new_y), Image.ANTIALIAS)
            resized_image.save(self.avatar.path)
        return article

    # 图像处理的轮子
    # avatar = ProcessedImageField(
    #     upload_to='article/%Y%m%d',
    #     processors=[ResizeToFit(width=400)],
    #     format='JPEG',
    #     options={'quality': 100},
    # )



    # 内部类 class Meta 用于给 model 定义元数据(外加功能)
    class Meta:
        """ordering 指定模型返回的数据的排列顺序
            保证了最新的文章总是在网页的最上方
        """
        # '-created' 表明数据应该以倒序排列
        ordering = ('-created',)
    def __str__(self):
        # return self.title 将文章标题返回
        return self.title
    def get_absolute_url(self):
        return reverse('article:article_detail', args=[self.id])

    column = models.ForeignKey(
        ArticleColumn,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='article'
    )


# Create your models here.
