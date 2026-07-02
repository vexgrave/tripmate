from django import forms

from .models import Trip


class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = [
            'title', 'description', 'image',
            'departure_city', 'destination', 'date', 'time',
            'budget', 'max_participants', 'category', 'transport',
            'requirements', 'interests', 'status',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'departure_city': forms.TextInput(attrs={'class': 'form-control'}),
            'destination': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'transport': forms.Select(attrs={'class': 'form-select'}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'interests': forms.CheckboxSelectMultiple,
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class TripCreateForm(TripForm):
    """При создании поездки статус всегда 'active' и не выбирается пользователем."""

    class Meta(TripForm.Meta):
        fields = [f for f in TripForm.Meta.fields if f != 'status']


class TripFilterForm(forms.Form):
    q = forms.CharField(required=False, label='Поиск', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Название или направление'}))
    departure_city = forms.CharField(required=False, label='Город отправления', widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    destination = forms.CharField(required=False, label='Направление', widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    date_from = forms.DateField(required=False, label='Дата от', widget=forms.DateInput(
        attrs={'class': 'form-control', 'type': 'date'}))
    date_to = forms.DateField(required=False, label='Дата до', widget=forms.DateInput(
        attrs={'class': 'form-control', 'type': 'date'}))
    budget_max = forms.IntegerField(required=False, label='Бюджет до', widget=forms.NumberInput(
        attrs={'class': 'form-control'}))
    category = forms.ChoiceField(required=False, label='Категория',
                                  choices=[('', 'Любая')] + list(Trip.Category.choices),
                                  widget=forms.Select(attrs={'class': 'form-select'}))
    transport = forms.ChoiceField(required=False, label='Транспорт',
                                   choices=[('', 'Любой')] + list(Trip.Transport.choices),
                                   widget=forms.Select(attrs={'class': 'form-select'}))
    interest = forms.ModelChoiceField(
        required=False, label='Интерес', queryset=None,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from accounts.models import Interest
        self.fields['interest'].queryset = Interest.objects.all()
