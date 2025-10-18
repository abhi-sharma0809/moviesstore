from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, MoviePetition, PetitionVote, MovieRating, GeographicRegion, MoviePurchase
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Sum, Avg
from django.http import JsonResponse

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term, amount_left__gt=0)
    else:
        movies = Movie.objects.filter(amount_left__gt=0)

    template_data = {}
    template_data['title'] = 'Movies - Georgia Tech Movie Store'
    template_data['movies'] = movies
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)
    
    # Get user's rating if they're logged in
    user_rating = None
    if request.user.is_authenticated:
        try:
            user_rating = MovieRating.objects.get(movie=movie, user=request.user)
        except MovieRating.DoesNotExist:
            user_rating = None

    template_data = {}
    template_data['title'] = f'{movie.name} - Georgia Tech Movie Store'
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    template_data['user_rating'] = user_rating
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)

    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review - Georgia Tech Movie Store'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

# Petition views
def petition_list(request):
    """Display all movie petitions ordered by vote count"""
    petitions = MoviePetition.objects.annotate(
        yes_votes=Count('votes', filter=Q(votes__vote_type='yes')),
        no_votes=Count('votes', filter=Q(votes__vote_type='no'))
    ).order_by('-yes_votes', '-created_at')
    
    template_data = {}
    template_data['title'] = 'Movie Petitions - Georgia Tech Movie Store'
    template_data['petitions'] = petitions
    return render(request, 'movies/petition_list.html', {'template_data': template_data})

@login_required
def create_petition(request):
    """Create a new movie petition"""
    if request.method == 'POST':
        movie_name = request.POST.get('movie_name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if movie_name and description:
            # Check if a petition for this movie already exists
            existing_petition = MoviePetition.objects.filter(movie_name__iexact=movie_name).first()
            if existing_petition:
                messages.error(request, 'A petition for this movie already exists!')
                return render(request, 'movies/create_petition.html', {
                    'template_data': {
                        'title': 'Create Movie Petition - Georgia Tech Movie Store',
                        'movie_name': movie_name,
                        'description': description
                    }
                })
            
            petition = MoviePetition()
            petition.movie_name = movie_name
            petition.description = description
            petition.created_by = request.user
            petition.save()
            
            messages.success(request, f'Petition for "{movie_name}" has been created successfully!')
            return redirect('movies.petition_list')
        else:
            messages.error(request, 'Please fill in both movie name and description.')
    
    template_data = {}
    template_data['title'] = 'Create Movie Petition - Georgia Tech Movie Store'
    return render(request, 'movies/create_petition.html', {'template_data': template_data})

def petition_detail(request, petition_id):
    """Display details of a specific petition"""
    petition = get_object_or_404(MoviePetition, id=petition_id)
    
    # Get user's vote if they're logged in
    user_vote = None
    if request.user.is_authenticated:
        try:
            user_vote = PetitionVote.objects.get(petition=petition, user=request.user)
        except PetitionVote.DoesNotExist:
            user_vote = None
    
    template_data = {}
    template_data['title'] = f'Petition: {petition.movie_name} - Georgia Tech Movie Store'
    template_data['petition'] = petition
    template_data['user_vote'] = user_vote
    return render(request, 'movies/petition_detail.html', {'template_data': template_data})

@login_required
def vote_petition(request, petition_id):
    """Vote on a petition"""
    petition = get_object_or_404(MoviePetition, id=petition_id)
    
    if request.method == 'POST':
        vote_type = request.POST.get('vote_type')
        
        if vote_type in ['yes', 'no']:
            # Check if user already voted
            existing_vote = PetitionVote.objects.filter(petition=petition, user=request.user).first()
            
            if existing_vote:
                # Update existing vote
                existing_vote.vote_type = vote_type
                existing_vote.save()
                messages.info(request, f'Your vote has been updated to {vote_type}.')
            else:
                # Create new vote
                vote = PetitionVote()
                vote.petition = petition
                vote.user = request.user
                vote.vote_type = vote_type
                vote.save()
                messages.success(request, f'Thank you for voting {vote_type}!')
            
            return redirect('movies.petition_detail', petition_id=petition_id)
    
    return redirect('movies.petition_detail', petition_id=petition_id)

# Rating views
@login_required
def rate_movie(request, movie_id):
    """Rate a movie with 1-5 stars"""
    movie = get_object_or_404(Movie, id=movie_id)
    
    if request.method == 'POST':
        rating_value = request.POST.get('rating')
        
        if rating_value and rating_value.isdigit():
            rating_value = int(rating_value)
            if 1 <= rating_value <= 5:
                # Check if user already rated this movie
                existing_rating = MovieRating.objects.filter(movie=movie, user=request.user).first()
                
                if existing_rating:
                    # Update existing rating
                    existing_rating.rating = rating_value
                    existing_rating.save()
                    messages.info(request, f'Your rating for "{movie.name}" has been updated to {rating_value} stars.')
                else:
                    # Create new rating
                    rating = MovieRating()
                    rating.movie = movie
                    rating.user = request.user
                    rating.rating = rating_value
                    rating.save()
                    messages.success(request, f'Thank you for rating "{movie.name}" {rating_value} stars!')
                
                return redirect('movies.show', id=movie_id)
    
    return redirect('movies.show', id=movie_id)

# Local Popularity Map views
def local_popularity_map(request):
    """Display the local popularity map"""
    regions = GeographicRegion.objects.all()
    
    # Get trending movies by region
    region_data = []
    for region in regions:
        # Get top 5 movies by purchase count in this region
        top_movies = Movie.objects.annotate(
            region_purchases=Sum('purchases__quantity', filter=Q(purchases__region=region))
        ).filter(region_purchases__gt=0).order_by('-region_purchases')[:5]
        
        region_data.append({
            'region': region,
            'top_movies': top_movies,
            'total_purchases': sum(movie.region_purchases for movie in top_movies)
        })
    
    template_data = {}
    template_data['title'] = 'Local Popularity Map - Georgia Tech Movie Store'
    template_data['regions'] = region_data
    
    return render(request, 'movies/local_popularity_map.html', {'template_data': template_data})

def region_detail(request, region_id):
    """Display detailed trending movies for a specific region"""
    region = get_object_or_404(GeographicRegion, id=region_id)
    
    # Get all movies with their purchase counts in this region
    movies = Movie.objects.annotate(
        region_purchases=Sum('purchases__quantity', filter=Q(purchases__region=region)),
        avg_rating=Avg('ratings__rating')
    ).filter(region_purchases__gt=0).order_by('-region_purchases')
    
    template_data = {}
    template_data['title'] = f'Trending Movies in {region.name} - Georgia Tech Movie Store'
    template_data['region'] = region
    template_data['movies'] = movies
    
    return render(request, 'movies/region_detail.html', {'template_data': template_data})

def region_data_api(request, region_id):
    """API endpoint to get region data for map markers"""
    region = get_object_or_404(GeographicRegion, id=region_id)
    
    # Get top movies in this region
    top_movies = Movie.objects.annotate(
        region_purchases=Sum('purchases__quantity', filter=Q(purchases__region=region))
    ).filter(region_purchases__gt=0).order_by('-region_purchases')[:5]
    
    data = {
        'region': {
            'id': region.id,
            'name': region.name,
            'latitude': region.latitude,
            'longitude': region.longitude,
            'zoom_level': region.zoom_level
        },
        'top_movies': [
            {
                'id': movie.id,
                'name': movie.name,
                'purchases': movie.region_purchases,
                'average_rating': movie.average_rating,
                'rating_count': movie.rating_count
            }
            for movie in top_movies
        ]
    }
    
    return JsonResponse(data)