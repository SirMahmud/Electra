from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .decorators import voter_required, admin_required, super_admin_required
from accounts.models import User
from accounts.forms import UserRoleForm
from elections.models import Election
from votes.models import Vote

def home_view(request):
    """Home page - redirects based on user role or shows landing page"""
    if request.user.is_authenticated:
        # Debug output
        print("="*50)
        print(f"User: {request.user.email}")
        print(f"Role: {request.user.role}")
        print(f"Is super admin: {request.user.is_super_admin()}")
        print(f"Is admin: {request.user.is_admin()}")
        print(f"Is voter: {request.user.is_voter()}")
        print("="*50)
        
        if request.user.is_super_admin():
            print("Redirecting to super_admin_dashboard")
            return redirect('voters:super_admin_dashboard')
        elif request.user.is_admin():
            print("Redirecting to admin_dashboard")
            return redirect('voters:admin_dashboard')
        else:
            print("Redirecting to voter_dashboard")
            return redirect('voters:voter_dashboard')
    
    # Show welcome page for guests
    return render(request, 'home.html')

@login_required
@voter_required
def voter_dashboard(request):
    """Voter dashboard - view and participate in elections"""
    # Show elections that are visible to voters (both upcoming and active)
    upcoming_elections = Election.objects.filter(
        status='upcoming',
        visible_to_voters=True
    ).order_by('start_date')
    
    active_elections = Election.objects.filter(
        status='active',
        visible_to_voters=True
    ).order_by('-created_at')
    
    # Show ended elections where results are published
    ended_elections = Election.objects.filter(
        status='ended',
        results_published=True,
        visible_to_voters=True
    ).order_by('-created_at')
    
    # Build election progress for active elections only
    election_progress = []
    for election in active_elections:
        total_positions = election.positions.count()
        voted_positions = Vote.objects.filter(
            user=request.user,
            election=election
        ).values('position').distinct().count()
        
        remaining = total_positions - voted_positions
        progress_percent = (voted_positions / total_positions * 100) if total_positions > 0 else 0
        completed = voted_positions == total_positions
        
        election_progress.append({
            'election': election,
            'total_positions': total_positions,
            'voted_positions': voted_positions,
            'remaining': remaining,
            'progress_percent': progress_percent,
            'completed': completed,
        })
    
    context = {
        'upcoming_elections': upcoming_elections,  # Add this
        'election_progress': election_progress,
        'ended_elections': ended_elections,
    }
    return render(request, 'voters/voter_dashboard.html', context)

@login_required
@admin_required
def admin_dashboard(request):
    """Admin dashboard - view users and live election charts"""
    # Exclude super admins from the user list for regular admins
    if request.user.is_super_admin():
        users = User.objects.all().order_by('-date_joined')
    else:
        # Regular admins should not see super admins
        users = User.objects.exclude(role='super_admin').order_by('-date_joined')
    
    active_elections = Election.objects.filter(status='active')
    
    context = {
        'users': users,
        'active_elections': active_elections,
        'total_users': users.count(),
        'total_voters': users.filter(role='voter').count(),
        'total_admins': users.filter(role='admin').count(),
    }
    return render(request, 'voters/admin_dashboard.html', context)

@login_required
@super_admin_required
def super_admin_dashboard(request):
    """Super admin dashboard - full control panel"""
    elections = Election.objects.all()
    users = User.objects.all()
    total_votes = Vote.objects.count()
    
    context = {
        'elections': elections,
        'users': users,
        'total_elections': elections.count(),
        'total_users': users.count(),
        'total_votes': total_votes,
        'active_elections': elections.filter(status='active').count(),
    }
    return render(request, 'voters/super_admin_dashboard.html', context)


@login_required
@super_admin_required
def manage_users(request):
    """Manage all users"""
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'voters/manage_users.html', {'users': users})


@login_required
@super_admin_required
def change_user_role(request, pk):
    """Change a user's role"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = UserRoleForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Role updated for {user.get_full_name()}!'
            )
            return redirect('voters:manage_users')
    else:
        form = UserRoleForm(instance=user)
    
    return render(request, 'voters/change_user_role.html', {
        'form': form,
        'user_obj': user
    })

