from django import forms
from .models import Contestant, Position


class PositionForm(forms.ModelForm):
    """Form for creating and editing positions"""
    
    class Meta:
        model = Position
        fields = ['title', 'description', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ContestantForm(forms.ModelForm):
    """Form for creating and editing contestants"""
    
    class Meta:
        model = Contestant
        fields = ['position', 'name', 'party', 'bio', 'photo', 'order']
        widgets = {
            'position': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'party': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        election = kwargs.pop('election', None)
        super().__init__(*args, **kwargs)
        
        # Filter positions by election
        if election:
            self.fields['position'].queryset = Position.objects.filter(
                election=election
            )
        else:
            self.fields['position'].queryset = Position.objects.none()