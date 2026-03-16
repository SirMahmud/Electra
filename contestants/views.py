from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Contestant, Position
from .forms import ContestantForm, PositionForm
from elections.models import Election
from voters.decorators import super_admin_required


# ============= Position Views =============

@login_required
@super_admin_required
def add_position(request, election_pk):
    """Add a position to an election"""
    election = get_object_or_404(Election, pk=election_pk)
    
    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            position = form.save(commit=False)
            position.election = election
            position.save()
            messages.success(
                request,
                f'Position "{position.title}" added successfully!'
            )
            return redirect('elections:manage_election', pk=election.pk)
    else:
        form = PositionForm()
    
    return render(request, 'contestants/add_position.html', {
        'form': form,
        'election': election
    })


@login_required
@super_admin_required
def edit_position(request, pk):
    """Edit a position"""
    position = get_object_or_404(Position, pk=pk)
    
    if request.method == 'POST':
        form = PositionForm(request.POST, instance=position)
        if form.is_valid():
            form.save()
            messages.success(request, 'Position updated successfully!')
            return redirect('elections:manage_election', pk=position.election.pk)
    else:
        form = PositionForm(instance=position)
    
    return render(request, 'contestants/edit_position.html', {
        'form': form,
        'position': position
    })


@login_required
@super_admin_required
def delete_position(request, pk):
    """Delete a position"""
    position = get_object_or_404(Position, pk=pk)
    election = position.election
    
    if request.method == 'POST':
        title = position.title
        position.delete()
        messages.success(request, f'Position "{title}" deleted successfully!')
        return redirect('elections:manage_election', pk=election.pk)
    
    return render(request, 'contestants/delete_position.html', {
        'position': position
    })


# ============= Contestant Views =============

@login_required
@super_admin_required
def add_contestant(request, election_pk):
    """Add a contestant to an election"""
    election = get_object_or_404(Election, pk=election_pk)
    
    # Check if election has positions
    if not election.positions.exists():
        messages.warning(
            request,
            'Please add at least one position before adding contestants.'
        )
        return redirect('elections:manage_election', pk=election.pk)
    
    if request.method == 'POST':
        form = ContestantForm(request.POST, request.FILES, election=election)
        if form.is_valid():
            contestant = form.save(commit=False)
            contestant.election = election
            contestant.save()
            messages.success(
                request,
                f'Contestant "{contestant.name}" added successfully!'
            )
            return redirect('elections:manage_election', pk=election.pk)
    else:
        form = ContestantForm(election=election)
    
    return render(request, 'contestants/add_contestant.html', {
        'form': form,
        'election': election
    })


@login_required
@super_admin_required
def edit_contestant(request, pk):
    """Edit a contestant"""
    contestant = get_object_or_404(Contestant, pk=pk)
    
    if request.method == 'POST':
        form = ContestantForm(
            request.POST,
            request.FILES,
            instance=contestant,
            election=contestant.election
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Contestant updated successfully!')
            return redirect('elections:manage_election', pk=contestant.election.pk)
    else:
        form = ContestantForm(instance=contestant, election=contestant.election)
    
    return render(request, 'contestants/edit_contestant.html', {
        'form': form,
        'contestant': contestant
    })


@login_required
@super_admin_required
def delete_contestant(request, pk):
    """Delete a contestant"""
    contestant = get_object_or_404(Contestant, pk=pk)
    election = contestant.election
    
    if request.method == 'POST':
        name = contestant.name
        contestant.delete()
        messages.success(request, f'Contestant "{name}" deleted successfully!')
        return redirect('elections:manage_election', pk=election.pk)
    
    return render(request, 'contestants/delete_contestant.html', {
        'contestant': contestant
    })