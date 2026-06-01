from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    # Honeypot: trường ẩn, người dùng thật để trống; bot thường tự điền.
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'tabindex': '-1', 'autocomplete': 'off',
            'style': 'position:absolute;left:-9999px;top:-9999px;',
            'aria-hidden': 'true',
        }),
        label='',
    )

    class Meta:
        model = ContactMessage
        fields = ('full_name', 'email', 'phone', 'company', 'subject', 'message')
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Họ và tên *'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 'placeholder': 'Email *'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Số điện thoại'
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Tên công ty'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Chủ đề *'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 5, 'placeholder': 'Nội dung tin nhắn *'
            }),
        }

    def clean_website(self):
        # Nếu honeypot có dữ liệu → là bot, từ chối âm thầm.
        if self.cleaned_data.get('website'):
            raise forms.ValidationError('Phát hiện spam.')
        return ''
