from django import forms

from .models import Application


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Расскажите организатору, почему хотите поехать (необязательно)',
            }),
        }
