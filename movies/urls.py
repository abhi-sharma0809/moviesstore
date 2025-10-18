from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='movies.index'),
    path('<int:id>/', views.show, name='movies.show'),
    path('<int:id>/review/create/', views.create_review, name='movies.create_review'),
    path('<int:id>/review/<int:review_id>/edit/', views.edit_review, name='movies.edit_review'),
    path('<int:id>/review/<int:review_id>/delete/', views.delete_review, name='movies.delete_review'),
    # Rating URLs
    path('<int:movie_id>/rate/', views.rate_movie, name='movies.rate_movie'),
    # Petition URLs
    path('petitions/', views.petition_list, name='movies.petition_list'),
    path('petitions/create/', views.create_petition, name='movies.create_petition'),
    path('petitions/<int:petition_id>/', views.petition_detail, name='movies.petition_detail'),
    path('petitions/<int:petition_id>/vote/', views.vote_petition, name='movies.vote_petition'),
    # Local Popularity Map URLs
    path('local-popularity/', views.local_popularity_map, name='movies.local_popularity_map'),
    path('region/<int:region_id>/', views.region_detail, name='movies.region_detail'),
    path('api/region/<int:region_id>/', views.region_data_api, name='movies.region_data_api'),
]