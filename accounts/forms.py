from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User, VoterIDRegistry


class UserRegistrationForm(forms.ModelForm):
    """Form for user registration"""
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'voter_id']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'voter_id': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email
    
    def clean_voter_id(self):
        """Validate voter ID against registry"""
        voter_id = self.cleaned_data.get('voter_id')
        
        # Check if voter ID already used by another user
        if User.objects.filter(voter_id=voter_id).exists():
            raise forms.ValidationError('This Voter ID is already registered.')
        
        # Check if voter ID exists in registry
        try:
            registry_entry = VoterIDRegistry.objects.get(voter_id=voter_id)
        except VoterIDRegistry.DoesNotExist:
            raise forms.ValidationError(
                'This Voter ID is not recognized. Please contact the administrator.'
            )
        
        # Check if voter ID is available
        if registry_entry.status == 'used':
            raise forms.ValidationError('This Voter ID has already been used.')
        elif registry_entry.status == 'blocked':
            raise forms.ValidationError(
                'This Voter ID is blocked. Please contact the administrator.'
            )
        elif registry_entry.status != 'available':
            raise forms.ValidationError('This Voter ID is not available for registration.')
        
        return voter_id
    
    def clean_password2(self):
        """Validate password confirmation"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')
        
        return password2
    
    def save(self, commit=True):
        """Save user and mark voter ID as used"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        
        if commit:
            user.save()
            
            # Mark voter ID as used
            try:
                registry_entry = VoterIDRegistry.objects.get(
                    voter_id=self.cleaned_data['voter_id']
                )
                registry_entry.mark_as_used(user)
            except VoterIDRegistry.DoesNotExist:
                pass
        
        return user


class UserLoginForm(AuthenticationForm):
    """Custom login form"""
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


class UserRoleForm(forms.ModelForm):
    """Form for changing user role"""
    
    class Meta:
        model = User
        fields = ['role']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
        }


class VoterIDRegistryForm(forms.ModelForm):
    """Form for adding voter IDs to registry"""
    
    class Meta:
        model = VoterIDRegistry
        fields = ['voter_id', 'status', 'notes']
        widgets = {
            'voter_id': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_voter_id(self):
        """Validate voter ID uniqueness"""
        voter_id = self.cleaned_data.get('voter_id')
        
        # Check if this is an update (instance has pk)
        if self.instance and self.instance.pk:
            # Updating existing - check uniqueness excluding current instance
            if VoterIDRegistry.objects.filter(voter_id=voter_id).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('This Voter ID already exists in the registry.')
        else:
            # Creating new - check uniqueness
            if VoterIDRegistry.objects.filter(voter_id=voter_id).exists():
                raise forms.ValidationError('This Voter ID already exists in the registry.')
        
        return voter_id

class BulkVoterIDUploadForm(forms.Form):
    """Form for bulk upload of voter IDs"""
    
    voter_ids = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Enter one Voter ID per line, e.g.:\nVOTER001\nVOTER002\nVOTER003'
        }),
        help_text='Enter one Voter ID per line'
    )
    
    def clean_voter_ids(self):
        """Validate and parse voter IDs"""
        voter_ids_text = self.cleaned_data.get('voter_ids', '')
        voter_ids = [vid.strip() for vid in voter_ids_text.split('\n') if vid.strip()]
        
        if not voter_ids:
            raise forms.ValidationError('Please enter at least one Voter ID.')
        
        # Check for duplicates in input
        duplicates = [vid for vid in voter_ids if voter_ids.count(vid) > 1]
        if duplicates:
            raise forms.ValidationError(
                f'Duplicate Voter IDs in your list: {", ".join(set(duplicates))}'
            )
        
        # Check which IDs already exist
        existing = VoterIDRegistry.objects.filter(voter_id__in=voter_ids)
        if existing.exists():
            existing_ids = [e.voter_id for e in existing]
            raise forms.ValidationError(
                f'These Voter IDs already exist in the registry: {", ".join(existing_ids)}'
            )
        
        return voter_ids

        