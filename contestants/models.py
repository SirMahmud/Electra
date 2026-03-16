from django.db import models
from elections.models import Election


class Position(models.Model):
    """Position model - e.g., President, Vice President, Secretary"""
    
    election = models.ForeignKey(
        Election,
        on_delete=models.CASCADE,
        related_name='positions'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Position'
        verbose_name_plural = 'Positions'
        ordering = ['election', 'order', 'title']
        unique_together = [['election', 'title']]
    
    def __str__(self):
        return f"{self.title} - {self.election.title}"
    
    def get_vote_count(self):
        """Get total votes cast for this position"""
        return self.votes.count()
    
    def get_contestants(self):
        """Get all contestants for this position"""
        return self.contestants.all()


class Contestant(models.Model):
    """Contestant model linked to a specific position"""
    
    election = models.ForeignKey(
        Election,
        on_delete=models.CASCADE,
        related_name='contestants'
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.CASCADE,
        related_name='contestants',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=200)
    party = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='contestants/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Contestant'
        verbose_name_plural = 'Contestants'
        ordering = ['election', 'position', 'order', 'name']
        unique_together = [['election', 'position', 'name']]
    
    def __str__(self):
        if self.position:
            return f"{self.name} ({self.position.title}) - {self.election.title}"
        return f"{self.name} - {self.election.title}"
    
    def get_vote_count(self):
        """Get number of votes for this contestant"""
        return self.votes.count()