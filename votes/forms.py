from django import forms
from .models import Vote
from contestants.models import Contestant, Position


class VoteForm(forms.Form):
    """Form for casting a vote for a specific position"""
    
    contestant = forms.ModelChoiceField(
        queryset=Contestant.objects.none(),
        widget=forms.RadioSelect(),
        empty_label=None,
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        election = kwargs.pop('election', None)
        position = kwargs.pop('position', None)
        super().__init__(*args, **kwargs)
        
        # Filter contestants by election and position
        if election and position:
            self.fields['contestant'].queryset = Contestant.objects.filter(
                election=election,
                position=position
            )
        elif election:
            self.fields['contestant'].queryset = Contestant.objects.filter(
                election=election
            )