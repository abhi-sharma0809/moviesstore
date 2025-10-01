from django.db import models
from django.contrib.auth.models import User

class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='movie_images/')
    amount_left = models.PositiveIntegerField(default=0, help_text="Number of copies available for purchase")

    def __str__(self):
        return str(self.id) + ' - ' + self.name

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name

class MoviePetition(models.Model):
    id = models.AutoField(primary_key=True)
    movie_name = models.CharField(max_length=255, help_text="Name of the movie to be added")
    description = models.TextField(help_text="Why should this movie be added?")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='petitions_created')
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False, help_text="Whether this petition has been approved by admin")
    
    def __str__(self):
        return f"Petition for: {self.movie_name}"
    
    @property
    def vote_count(self):
        """Returns the total number of yes votes for this petition"""
        return self.votes.filter(vote_type='yes').count()
    
    @property
    def no_vote_count(self):
        """Returns the total number of no votes for this petition"""
        return self.votes.filter(vote_type='no').count()

class PetitionVote(models.Model):
    VOTE_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    
    id = models.AutoField(primary_key=True)
    petition = models.ForeignKey(MoviePetition, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='petition_votes')
    vote_type = models.CharField(max_length=3, choices=VOTE_CHOICES)
    voted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('petition', 'user')  # Each user can only vote once per petition
    
    def __str__(self):
        return f"{self.user.username} voted {self.vote_type} on {self.petition.movie_name}"