from django import forms
from .models import Election


class ElectionForm(forms.ModelForm):
    """Form for creating and editing elections"""
    
    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control', 
            'type': 'datetime-local'
        }),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control', 
            'type': 'datetime-local'
        }),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    
    class Meta:
        model = Election
        fields = ['title', 'description', 'start_date', 'end_date', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }