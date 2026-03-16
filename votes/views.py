from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Vote
from .forms import VoteForm
from elections.models import Election
from contestants.models import Position
from voters.decorators import voter_required


@login_required
@voter_required
def vote_view(request, election_pk):
    """Cast votes in an election - one vote per position"""
    election = get_object_or_404(Election, pk=election_pk)
    
    # Check if election is active
    if not election.can_vote():
        messages.error(request, 'This election is not currently active.')
        return redirect('voters:voter_dashboard')
    
    # Get all positions for this election
    positions = election.positions.all()
    
    # Get positions user has already voted for
    voted_positions = Vote.objects.filter(
        user=request.user,
        election=election
    ).values_list('position_id', flat=True)
    
    # Get remaining positions to vote for
    remaining_positions = positions.exclude(id__in=voted_positions)
    
    # If user has voted for all positions, redirect
    if not remaining_positions.exists():
        messages.info(
            request,
            'You have already voted for all positions in this election.'
        )
        return redirect('voters:voter_dashboard')
    
    # Get the current position to vote for (first remaining)
    current_position = remaining_positions.first()
    
    if request.method == 'POST':
        form = VoteForm(
            request.POST,
            election=election,
            position=current_position
        )
        if form.is_valid():
            contestant = form.cleaned_data['contestant']
            
            try:
                # Create the vote
                Vote.objects.create(
                    user=request.user,
                    election=election,
                    position=current_position,
                    contestant=contestant
                )
                
                # Check if there are more positions to vote for
                new_remaining = positions.exclude(
                    id__in=Vote.objects.filter(
                        user=request.user,
                        election=election
                    ).values_list('position_id', flat=True)
                )
                
                if new_remaining.exists():
                    messages.success(
                        request,
                        f'Vote recorded for {current_position.title}! '
                        f'Please vote for the next position.'
                    )
                    # Redirect back to vote for next position
                    return redirect('votes:vote', election_pk=election.pk)
                else:
                    messages.success(
                        request,
                        'All your votes have been recorded successfully!'
                    )
                    return redirect('voters:voter_dashboard')
            
            except Exception as e:
                messages.error(request, f'Error recording vote: {str(e)}')
        else:
            messages.error(request, 'Please select a contestant.')
    else:
        form = VoteForm(election=election, position=current_position)
    
    context = {
        'election': election,
        'positions': positions,
        'current_position': current_position,
        'voted_positions': list(voted_positions),
        'remaining_count': remaining_positions.count(),
        'total_positions': positions.count(),
        'form': form,
    }
    return render(request, 'votes/vote.html', context)

    