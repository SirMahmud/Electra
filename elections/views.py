from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Election
from .forms import ElectionForm
from voters.decorators import super_admin_required, admin_required


@login_required
@super_admin_required
def create_election(request):
    """Create a new election"""
    if request.method == 'POST':
        form = ElectionForm(request.POST)
        if form.is_valid():
            election = form.save(commit=False)
            election.created_by = request.user
            election.save()
            messages.success(
                request,
                f'Election "{election.title}" created successfully!'
            )
            return redirect('elections:manage_election', pk=election.pk)
    else:
        form = ElectionForm()
    
    return render(request, 'elections/create_election.html', {'form': form})


@login_required
@super_admin_required
def manage_election(request, pk):
    """Manage an election, its positions and contestants"""
    election = get_object_or_404(Election, pk=pk)
    positions = election.positions.prefetch_related('contestants').all()
    
    context = {
        'election': election,
        'positions': positions,
    }
    return render(request, 'elections/manage_election.html', context)


@login_required
@super_admin_required
def edit_election(request, pk):
    """Edit an election"""
    election = get_object_or_404(Election, pk=pk)
    
    if request.method == 'POST':
        form = ElectionForm(request.POST, instance=election)
        if form.is_valid():
            form.save()
            messages.success(request, 'Election updated successfully!')
            return redirect('elections:manage_election', pk=election.pk)
    else:
        form = ElectionForm(instance=election)
    
    return render(request, 'elections/edit_election.html', {
        'form': form,
        'election': election
    })


@login_required
@super_admin_required
def delete_election(request, pk):
    """Delete an election"""
    election = get_object_or_404(Election, pk=pk)
    
    if request.method == 'POST':
        title = election.title
        election.delete()
        messages.success(request, f'Election "{title}" deleted successfully!')
        return redirect('voters:super_admin_dashboard')
    
    return render(request, 'elections/delete_election.html', {
        'election': election
    })


@login_required
@super_admin_required
def start_election(request, pk):
    """Start an election"""
    election = get_object_or_404(Election, pk=pk)
    election.status = 'active'
    
    # Auto-set start date to now if it's in the future
    if election.start_date > timezone.now():
        election.start_date = timezone.now()
    
    election.save()
    messages.success(request, f'Election "{election.title}" has been started!')
    return redirect('elections:manage_election', pk=election.pk)


@login_required
@super_admin_required
def end_election(request, pk):
    """End an election"""
    election = get_object_or_404(Election, pk=pk)
    election.status = 'ended'
    election.save()
    messages.success(request, f'Election "{election.title}" has been ended!')
    return redirect('elections:manage_election', pk=election.pk)


@login_required
@super_admin_required
def publish_results(request, pk):
    """Publish election results"""
    election = get_object_or_404(Election, pk=pk)
    
    if election.status != 'ended':
        messages.error(
            request,
            'You can only publish results for ended elections.'
        )
        return redirect('elections:manage_election', pk=election.pk)
    
    election.results_published = True
    election.save()
    messages.success(
        request,
        f'Results for "{election.title}" have been published!'
    )
    return redirect('elections:manage_election', pk=election.pk)


@login_required
def election_results(request, pk):
    """View election results (only if published)"""
    election = get_object_or_404(Election, pk=pk)

    if not election.results_published:
        messages.error(
            request,
            'Results for this election have not been published yet.'
        )
        return redirect('home')

    results_by_position = election.get_results_by_position()

    # Debug: print to terminal to verify data
    if results_by_position:
        for pos_data in results_by_position:
            print(f"Position: {pos_data['position'].title}")
            print(f"Results: {pos_data['results']}")
            print(f"Total votes: {pos_data['total_votes']}")

    context = {
        'election': election,
        'results_by_position': results_by_position,
        'total_votes': election.get_total_votes(),
    }
    return render(request, 'elections/results.html', context)

@login_required
def get_live_results(request, pk):
    """Get live voting results grouped by position"""
    election = get_object_or_404(Election, pk=pk)
    
    if not (request.user.is_admin() or request.user.is_super_admin()):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    positions_data = []
    for position in election.positions.all():
        contestants_data = []
        for contestant in position.contestants.all():
            contestants_data.append({
                'id': contestant.id,
                'name': contestant.name,
                'party': contestant.party,
                'votes': contestant.get_vote_count(),
            })
        positions_data.append({
            'id': position.id,
            'title': position.title,
            'total_votes': position.get_vote_count(),
            'contestants': contestants_data,
        })

@login_required
@super_admin_required
def toggle_visibility(request, pk):
    """Toggle election visibility to voters"""
    election = get_object_or_404(Election, pk=pk)
    
    # Toggle visibility
    election.visible_to_voters = not election.visible_to_voters
    election.save()
    
    status = "visible" if election.visible_to_voters else "hidden"
    messages.success(request, f'Election "{election.title}" is now {status} to voters.')
    
    return redirect('voters:super_admin_dashboard')
    
    return JsonResponse({
        'election': {
            'id': election.id,
            'title': election.title,
            'status': election.status,
        },
        'positions': positions_data,
        'total_votes': election.get_total_votes(),
        'timestamp': timezone.now().isoformat(),
    })