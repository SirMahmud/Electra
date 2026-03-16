from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import User
from elections.models import Election
from contestants.models import Contestant, Position


class Vote(models.Model):
    """Vote model - one vote per user per position per election"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    election = models.ForeignKey(
        Election,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.CASCADE,
        related_name='votes',
        null=True,
        blank=True
    )
    contestant = models.ForeignKey(
        Contestant,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    voted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Vote'
        verbose_name_plural = 'Votes'
        # One vote per user per position per election
        unique_together = [['user', 'election', 'position']]
        ordering = ['-voted_at']
        indexes = [
            models.Index(fields=['election', 'position', 'contestant']),
            models.Index(fields=['user', 'election', 'position']),
        ]
    
    def __str__(self):
        return f"{self.user.voter_id} voted for {self.position} in {self.election.title}"
    
    def clean(self):
        """Validate vote"""
        # Check if contestant belongs to election
        if self.contestant.election != self.election:
            raise ValidationError('Contestant does not belong to this election')
        
        # Check if contestant belongs to the position
        if self.position and self.contestant.position != self.position:
            raise ValidationError('Contestant does not belong to this position')
        
        # Check if election is active
        if not self.election.can_vote():
            raise ValidationError('This election is not currently active')
        
        # Check if user already voted for this position
        if Vote.objects.filter(
            user=self.user,
            election=self.election,
            position=self.position
        ).exclude(pk=self.pk).exists():
            raise ValidationError('You have already voted for this position')