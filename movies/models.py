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
    
    @property
    def average_rating(self):
        """Calculate the average rating for this movie"""
        from django.db.models import Avg
        avg = self.ratings.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0
    
    @property
    def rating_count(self):
        """Get the total number of ratings for this movie"""
        return self.ratings.count()
    
    @property
    def stars_display(self):
        """Returns a string of stars for display based on average rating"""
        avg = self.average_rating
        if avg == 0:
            return "☆☆☆☆☆"
        full_stars = int(avg)
        half_star = 1 if avg - full_stars >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        return "★" * full_stars + "☆" * half_star + "☆" * empty_stars
    
    def get_popularity_in_region(self, region):
        """Get the popularity (purchase count) of this movie in a specific region"""
        return self.purchases.filter(region=region).aggregate(
            total=models.Sum('quantity')
        )['total'] or 0

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

class MovieRating(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    id = models.AutoField(primary_key=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movie_ratings')
    rating = models.IntegerField(choices=RATING_CHOICES)
    rated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('movie', 'user')  # Each user can only rate a movie once
    
    def __str__(self):
        return f"{self.user.username} rated {self.movie.name} {self.rating} stars"
    
    @property
    def stars_display(self):
        """Returns a string of stars for display"""
        return '★' * self.rating + '☆' * (5 - self.rating)

class GeographicRegion(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    latitude = models.FloatField(help_text="Center latitude for map display")
    longitude = models.FloatField(help_text="Center longitude for map display")
    zoom_level = models.IntegerField(default=10, help_text="Map zoom level for this region")
    
    def __str__(self):
        return self.name

class MoviePurchase(models.Model):
    id = models.AutoField(primary_key=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='purchases')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movie_purchases')
    region = models.ForeignKey(GeographicRegion, on_delete=models.CASCADE, related_name='purchases')
    purchase_date = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.user.username} purchased {self.movie.name} in {self.region.name}"