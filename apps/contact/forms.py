from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
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
