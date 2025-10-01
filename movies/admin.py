from django.contrib import admin
from .models import Movie, Review, MoviePetition, PetitionVote

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

admin.site.register(Movie, MovieAdmin)
admin.site.register(Review)
admin.site.register(MoviePetition, MoviePetitionAdmin)
admin.site.register(PetitionVote, PetitionVoteAdmin)