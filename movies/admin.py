from django.contrib import admin
from .models import Movie, Review, MoviePetition, PetitionVote, MovieRating, GeographicRegion, MoviePurchase

class MovieAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']
    list_display = ['name', 'price', 'amount_left']
    list_editable = ['amount_left']
    fields = ['name', 'price', 'description', 'image', 'amount_left']

class PetitionVoteInline(admin.TabularInline):
    model = PetitionVote
    extra = 0
    readonly_fields = ['user', 'vote_type', 'voted_at']

class MoviePetitionAdmin(admin.ModelAdmin):
    list_display = ['movie_name', 'created_by', 'created_at', 'vote_count', 'no_vote_count', 'is_approved']
    list_filter = ['created_at', 'is_approved']
    search_fields = ['movie_name', 'description', 'created_by__username']
    readonly_fields = ['created_at']
    list_editable = ['is_approved']
    inlines = [PetitionVoteInline]
    
    def vote_count(self, obj):
        return obj.vote_count
    vote_count.short_description = 'Yes Votes'
    
    def no_vote_count(self, obj):
        return obj.no_vote_count
    no_vote_count.short_description = 'No Votes'

class PetitionVoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'petition', 'vote_type', 'voted_at']
    list_filter = ['vote_type', 'voted_at']
    search_fields = ['user__username', 'petition__movie_name']
    readonly_fields = ['voted_at']

class MovieRatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'rating', 'rated_at']
    list_filter = ['rating', 'rated_at']
    search_fields = ['user__username', 'movie__name']
    readonly_fields = ['rated_at']

class GeographicRegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'latitude', 'longitude', 'zoom_level']
    search_fields = ['name']

class MoviePurchaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'region', 'quantity', 'purchase_date']
    list_filter = ['region', 'purchase_date']
    search_fields = ['user__username', 'movie__name', 'region__name']
    readonly_fields = ['purchase_date']

admin.site.register(Movie, MovieAdmin)
admin.site.register(Review)
admin.site.register(MoviePetition, MoviePetitionAdmin)
admin.site.register(PetitionVote, PetitionVoteAdmin)
admin.site.register(MovieRating, MovieRatingAdmin)
admin.site.register(GeographicRegion, GeographicRegionAdmin)
admin.site.register(MoviePurchase, MoviePurchaseAdmin)