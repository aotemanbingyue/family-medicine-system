from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, FamilyMedicine, SharePost, PostComment, CommentReply, GlobalMedicine, SystemAnnouncement, PrivateMessage, MedicalTip


def _bootstrap_class(attrs=None):
    base = attrs or {}
    base.setdefault('class', '')
    if 'form-control' not in base['class']:
        base['class'] = (base['class'] + ' form-control').strip()
    return base


class RegisterForm(UserCreationForm):
    phone = forms.CharField(max_length=11, required=False, label='手机号', widget=forms.TextInput(attrs=_bootstrap_class()))
    family_id = forms.CharField(max_length=20, required=False, label='家庭组ID', help_text='与家人填写相同ID即可成组', widget=forms.TextInput(attrs=_bootstrap_class()))

    class Meta:
        model = User
        fields = ('username', 'phone', 'family_id', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ('username', 'password1', 'password2'):
            if name in self.fields:
                self.fields[name].widget.attrs.update(_bootstrap_class())


class FamilyMedicineForm(forms.ModelForm):
    class Meta:
        model = FamilyMedicine
        fields = (
            'name',
            'global_info',
            'production_date',
            'expiration_date',
            'stock',
            'unit',
            'reminder_enabled',
            'daily_reminder_time',
            'dosage_note',
        )
        widgets = {
            'name': forms.TextInput(attrs=_bootstrap_class()),
            'global_info': forms.Select(attrs=_bootstrap_class()),
            'production_date': forms.DateInput(attrs=_bootstrap_class({'type': 'date'})),
            'expiration_date': forms.DateInput(attrs=_bootstrap_class({'type': 'date'})),
            'stock': forms.NumberInput(attrs=_bootstrap_class()),
            'unit': forms.TextInput(attrs=_bootstrap_class()),
            'reminder_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'daily_reminder_time': forms.TimeInput(attrs=_bootstrap_class({'type': 'time'})),
            'dosage_note': forms.TextInput(attrs=_bootstrap_class({'placeholder': '例如：每日晚饭后 1 次，每次 1 粒'})),
        }

    def clean(self):
        data = super().clean()
        if data.get("reminder_enabled") and not data.get("daily_reminder_time"):
            self.add_error("daily_reminder_time", "开启服药提醒时，请设置每日提醒时间。")
        return data


class SharePostForm(forms.ModelForm):
    class Meta:
        model = SharePost
        fields = ('medicine', 'title', 'content')
        widgets = {
            'medicine': forms.Select(attrs=_bootstrap_class()),
            'title': forms.TextInput(attrs=_bootstrap_class()),
            'content': forms.Textarea(attrs=_bootstrap_class()),
        }


class PostCommentForm(forms.ModelForm):
    class Meta:
        model = PostComment
        fields = ('content',)
        widgets = {'content': forms.Textarea(attrs=_bootstrap_class({'rows': 2, 'placeholder': '留言内容（如：我想联系您）'}))}


class CommentReplyForm(forms.ModelForm):
    class Meta:
        model = CommentReply
        fields = ('content',)
        widgets = {'content': forms.TextInput(attrs=_bootstrap_class({'placeholder': '回复内容'}))}


class GlobalMedicineForm(forms.ModelForm):
    class Meta:
        model = GlobalMedicine
        fields = ('name', 'category', 'barcode', 'description')
        widgets = {
            'name': forms.TextInput(attrs=_bootstrap_class()),
            'category': forms.Select(attrs=_bootstrap_class()),
            'barcode': forms.TextInput(attrs=_bootstrap_class()),
            'description': forms.Textarea(attrs=_bootstrap_class()),
        }


class FamilyGroupForm(forms.Form):
    """家庭组设置：创建新组 或 加入已有组。"""
    ACTION_CHOICES = [('create', '创建新家庭组'), ('join', '加入已有家庭组')]
    action = forms.ChoiceField(choices=ACTION_CHOICES, widget=forms.RadioSelect, label='操作')
    family_id = forms.CharField(max_length=20, required=False, label='家庭组ID',
        help_text='家人分享给您的家庭组ID，填写后即可加入',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例如：family_abc12345'}))

    def clean(self):
        data = super().clean()
        if data.get('action') == 'join' and not (data.get('family_id') or '').strip():
            self.add_error('family_id', '加入家庭组时请填写家庭组ID')
        return data


class SystemAnnouncementForm(forms.ModelForm):
    class Meta:
        model = SystemAnnouncement
        fields = ('title', 'content', 'is_pinned')
        widgets = {
            'title': forms.TextInput(attrs=_bootstrap_class({'placeholder': '公告标题'})),
            'content': forms.Textarea(attrs=_bootstrap_class({'rows': 5, 'placeholder': '公告内容'})),
        }


class PrivateMessageForm(forms.ModelForm):
    """
    私聊消息表单。

    说明：
    1. 仅暴露 content 字段，sender/receiver 在视图中根据当前会话自动赋值；
    2. 使用统一 Bootstrap 样式，保持界面风格一致。
    """
    class Meta:
        model = PrivateMessage
        fields = ("content",)
        widgets = {
            "content": forms.Textarea(
                attrs=_bootstrap_class(
                    {
                        "rows": 3,
                        "placeholder": "请输入要发送给管理员/用户的消息...",
                    }
                )
            )
        }


class MedicalTipForm(forms.ModelForm):
    class Meta:
        model = MedicalTip
        fields = ("tip_date", "title", "content")
        widgets = {
            "tip_date": forms.DateInput(attrs=_bootstrap_class({"type": "date"})),
            "title": forms.TextInput(attrs=_bootstrap_class({"placeholder": "例如：春季过敏用药注意事项"})),
            "content": forms.Textarea(attrs=_bootstrap_class({"rows": 5, "placeholder": "请输入医学常识科普内容..."})),
        }
