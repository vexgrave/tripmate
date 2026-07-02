from django import forms

from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'avatar', 'city', 'age', 'bio', 'interests',
            'telegram_url', 'vk_url', 'instagram_url', 'youtube_url', 'other_url',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'interests': forms.CheckboxSelectMultiple,
            'telegram_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://t.me/username'}),
            'vk_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://vk.com/id...'}),
            'instagram_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://instagram.com/...'}),
            'youtube_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://youtube.com/@...'}),
            'other_url': forms.URLInput(attrs={'class': 'form-control'}),
        }
