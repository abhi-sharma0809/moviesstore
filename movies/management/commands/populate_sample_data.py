from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from movies.models import GeographicRegion, Movie, MoviePurchase, MovieRating
import random

class Command(BaseCommand):
    help = 'Populate sample geographic regions and purchase data'

    def handle(self, *args, **options):
        # Create sample geographic regions around Georgia Tech
        regions_data = [
            {'name': 'Atlanta Downtown', 'lat': 33.7490, 'lng': -84.3880, 'zoom': 12},
            {'name': 'Midtown Atlanta', 'lat': 33.7849, 'lng': -84.3843, 'zoom': 13},
            {'name': 'Buckhead', 'lat': 33.8470, 'lng': -84.3659, 'zoom': 13},
            {'name': 'Decatur', 'lat': 33.7748, 'lng': -84.2963, 'zoom': 12},
            {'name': 'Sandy Springs', 'lat': 33.9304, 'lng': -84.3733, 'zoom': 12},
            {'name': 'Alpharetta', 'lat': 34.0754, 'lng': -84.2941, 'zoom': 11},
            {'name': 'Marietta', 'lat': 33.9526, 'lng': -84.5499, 'zoom': 12},
            {'name': 'Roswell', 'lat': 34.0232, 'lng': -84.3615, 'zoom': 12},
        ]
        
        # Create regions
        for region_data in regions_data:
            region, created = GeographicRegion.objects.get_or_create(
                name=region_data['name'],
                defaults={
                    'latitude': region_data['lat'],
                    'longitude': region_data['lng'],
                    'zoom_level': region_data['zoom']
                }
            )
            if created:
                self.stdout.write(f'Created region: {region.name}')
        
        # Get all movies and users
        movies = Movie.objects.all()
        users = User.objects.all()
        regions = GeographicRegion.objects.all()
        
        if not movies.exists():
            self.stdout.write('No movies found. Please add some movies first.')
            return
            
        if not users.exists():
            self.stdout.write('No users found. Please create some users first.')
            return
        
        # Create sample purchases
        purchase_count = 0
        for _ in range(50):  # Create 50 sample purchases
            movie = random.choice(movies)
            user = random.choice(users)
            region = random.choice(regions)
            quantity = random.randint(1, 3)
            
            purchase = MoviePurchase.objects.create(
                movie=movie,
                user=user,
                region=region,
                quantity=quantity
            )
            purchase_count += 1
        
        # Create sample ratings
        rating_count = 0
        for _ in range(30):  # Create 30 sample ratings
            movie = random.choice(movies)
            user = random.choice(users)
            rating_value = random.randint(1, 5)
            
            # Check if user already rated this movie
            if not MovieRating.objects.filter(movie=movie, user=user).exists():
                rating = MovieRating.objects.create(
                    movie=movie,
                    user=user,
                    rating=rating_value
                )
                rating_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {purchase_count} purchases and {rating_count} ratings'
            )
        )

