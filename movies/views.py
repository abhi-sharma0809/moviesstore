from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, MoviePetition, PetitionVote
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q

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

    template_data = {}
    template_data['title'] = f'{movie.name} - Georgia Tech Movie Store'
    template_data['movie'] = movie
    template_data['reviews'] = reviews
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