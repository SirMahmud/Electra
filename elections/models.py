from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from accounts.models import User


class Election(models.Model):
    """Election model"""


    visible_to_voters = models.BooleanField(default=False)

    
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('active', 'Active'),
        ('ended', 'Ended'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='upcoming'
    )
    results_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_elections'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Election'
        verbose_name_plural = 'Elections'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def clean(self):
        """Validate election dates"""
        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                raise ValidationError('End date must be after start date')

    def is_active(self):
        """Check if election is currently active"""
        return self.status == 'active'

    def can_vote(self):
        """Check if users can vote in this election"""
        return self.status == 'active'

    def get_total_votes(self):
        """Get total number of votes cast"""
        return self.votes.count()

    def get_results_by_position(self):
        """Get election results grouped by position"""
        if not self.results_published:
            return None

        results_by_position = []

        for position in self.positions.all().order_by('order'):
            position_results = []
            total_votes_for_position = position.get_vote_count()

            for contestant in position.contestants.all().order_by('order'):
                vote_count = contestant.get_vote_count()
                percentage = (
                    round((vote_count / total_votes_for_position) * 100, 2)
                ) if total_votes_for_position > 0 else 0

                position_results.append({
                    'contestant': contestant,
                    'votes': vote_count,
                    'percentage': percentage,
                })

            # Sort by votes descending
            position_results.sort(key=lambda x: x['votes'], reverse=True)

            # ========================================
            # CHECK FOR TIE - No winner if tied
            # ========================================
            winner = None
            is_tie = False

            if position_results:
                highest_votes = position_results[0]['votes']

                if highest_votes == 0:
                    # Nobody voted - no winner
                    winner = None
                    is_tie = False
                else:
                    # Count how many contestants have the highest votes
                    tied_contestants = [
                        r for r in position_results
                        if r['votes'] == highest_votes
                    ]

                    if len(tied_contestants) > 1:
                        # More than one has the same highest votes = TIE
                        winner = None
                        is_tie = True
                    else:
                        # Clear winner
                        winner = position_results[0]
                        is_tie = False

            results_by_position.append({
                'position': position,
                'results': position_results,
                'total_votes': total_votes_for_position,
                'winner': winner,
                'is_tie': is_tie,
                'tied_contestants': [
                    r for r in position_results
                    if r['votes'] == position_results[0]['votes']
                ] if is_tie else [],
            })

        return results_by_position


        