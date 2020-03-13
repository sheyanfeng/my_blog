from django import forms
from django.contrib.auth.models import User
from .models import UserInfo
from PIL import Image
class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        fields = ['avatar']

class PhotoForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = UserInfo
        fields = (
            'avatar',
            'x',
            'y',
            'width',
            'height',
        )

def save(self, commit=True, user_id=None):

    if UserInfo.objects.get(user_id=user_id):
        userinfo = UserInfo.objects.get(user_id=user_id)
        userinfo.avatar = super(PhotoForm, self).save(commit=False).avatar
    else:
        userinfo = super(PhotoForm, self).save(commit=False)
        userinfo.user_id = user_id

    userinfo.save()

    x = self.cleaned_data.get('x')
    y = self.cleaned_data.get('y')
    w = self.cleaned_data.get('width')
    h = self.cleaned_data.get('height')

    image = Image.open(userinfo.avatar)
    cropped_image = image.crop((x, y, w + x, h + y))
    resized_image = cropped_image.resize((150, 150), Image.ANTIALIAS)
    resized_image.save(userinfo.avatar.path)

    return userinfo










# class UserLoginForm(forms.Form):
#     username = forms.CharField()
#     password = forms.CharField()
#
# class UserRegisterForm(forms.ModelForm):
#     #后来输入的
#     password = forms.CharField()
#     password2 = forms.CharField()
#     #一开始有的
#     class Meta:
#         model = User
#         fields = ('username', 'email')
#     def clean_password2(self):
#         #先清空数据
#         data = self.cleaned_data
#         if data.get('password') == data.get('password2'):
#             return data.get('password')
#         else:
#             raise forms.ValidationError("密码输入不一致,请重试。")
# class ProfileForm(forms.ModelForm):
#     class Meta:
#         model = Profile
#         fields = ('phone', 'avatar', 'bio')
