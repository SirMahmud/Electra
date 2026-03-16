from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, VoterIDRegistry
from .forms import (
    UserRegistrationForm, 
    UserLoginForm, 
    UserRoleForm,
    VoterIDRegistryForm,
    BulkVoterIDUploadForm
)
from voters.decorators import super_admin_required


# ========================================
# USER AUTHENTICATION VIEWS
# ========================================

def register_view(request):
    """Register view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f'Welcome to ELECTRA, {user.get_full_name()}!'
            )
            return redirect('home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Login view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(
                    request,
                    f'Welcome back, {user.get_full_name()}!'
                )
                return redirect('home')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """Profile view"""
    return render(request, 'accounts/profile.html')


# ========================================
# VOTER ID MANAGEMENT VIEWS
# ========================================

@login_required
@super_admin_required
def manage_voter_ids(request):
    """View all voter IDs in registry"""
    voter_ids = VoterIDRegistry.objects.all().order_by('-created_at')
    
    stats = {
        'total': voter_ids.count(),
        'available': voter_ids.filter(status='available').count(),
        'used': voter_ids.filter(status='used').count(),
        'blocked': voter_ids.filter(status='blocked').count(),
    }
    
    context = {
        'voter_ids': voter_ids,
        'stats': stats,
    }
    return render(request, 'accounts/manage_voter_ids.html', context)


@login_required
@super_admin_required
def add_voter_id(request):
    """Add single voter ID to registry"""
    if request.method == 'POST':
        form = VoterIDRegistryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Voter ID added successfully!')
            return redirect('accounts:manage_voter_ids')
    else:
        form = VoterIDRegistryForm()
    
    return render(request, 'accounts/add_voter_id.html', {'form': form})


@login_required
@super_admin_required
def bulk_upload_voter_ids(request):
    """Bulk upload voter IDs"""
    if request.method == 'POST':
        form = BulkVoterIDUploadForm(request.POST)
        if form.is_valid():
            voter_ids = form.cleaned_data['voter_ids']
            
            # Create voter ID entries
            created_count = 0
            for voter_id in voter_ids:
                VoterIDRegistry.objects.create(
                    voter_id=voter_id,
                    status='available'
                )
                created_count += 1
            
            messages.success(
                request,
                f'{created_count} Voter IDs added successfully!'
            )
            return redirect('accounts:manage_voter_ids')
    else:
        form = BulkVoterIDUploadForm()
    
    return render(request, 'accounts/bulk_upload_voter_ids.html', {'form': form})


@login_required
@super_admin_required
def edit_voter_id(request, pk):
    """Edit voter ID status"""
    voter_id_entry = get_object_or_404(VoterIDRegistry, pk=pk)
    
    if request.method == 'POST':
        form = VoterIDRegistryForm(request.POST, instance=voter_id_entry)
        if form.is_valid():
            form.save()
            messages.success(request, 'Voter ID updated successfully!')
            return redirect('accounts:manage_voter_ids')
    else:
        form = VoterIDRegistryForm(instance=voter_id_entry)
    
    return render(request, 'accounts/edit_voter_id.html', {
        'form': form,
        'voter_id_entry': voter_id_entry
    })


@login_required
@super_admin_required
def delete_voter_id(request, pk):
    """Delete voter ID from registry"""
    voter_id_entry = get_object_or_404(VoterIDRegistry, pk=pk)
    
    if request.method == 'POST':
        voter_id_value = voter_id_entry.voter_id
        voter_id_entry.delete()
        messages.success(request, f'Voter ID "{voter_id_value}" deleted successfully!')
        return redirect('accounts:manage_voter_ids')
    
    return render(request, 'accounts/delete_voter_id.html', {
        'voter_id_entry': voter_id_entry
    })