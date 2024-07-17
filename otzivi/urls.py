# from django.contrib import admin
# from django.urls import path, include
# from django.contrib.auth import views as auth_views
# from myapp import views

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from myapp import views
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from myapp.views import my_set_language
urlpatterns = [
    path('set_language/', my_set_language, name='set_language'),
]

# urlpatterns = [
#     path('set_language/', set_language, name='set_language'),
#     path('admin/', admin.site.urls),
#     path('', views.index, name='index'),
#     path('api/reviews/', views.api_reviews, name='api_reviews'),
#     path('accounts/', include('django.contrib.auth.urls')),
#     path('register/', views.register, name='register'),
#     path('login/', views.login, name='login'),
#     path('profile/<str:username>/', views.profile, name='profile'),
#     path('add_review/', views.add_review, name='add_review'),

#     path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),
#     path('accounts/password_reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset_form.html', email_template_name='accounts/password_reset_email.html', subject_template_name='accounts/password_reset_subject.txt', success_url='/accounts/password_reset/done/'), name='password_reset'),
#     path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
#     path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html', success_url='/accounts/reset/done/'), name='password_reset_confirm'),
#     path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),

#     path('profile/<str:username>/edit/', views.edit_profile, name='edit_profile'),
#     path('edit_review/<int:review_id>/', views.edit_review, name='edit_review'),
#     path('api/load_more_reviews/', views.load_more_reviews, name='load_more_reviews'),
#     path('api/search_reviews/', views.search_reviews, name='search_reviews'),
#     path('company_ratings/', views.company_ratings, name='company_ratings'),
#     path('delete_review/<int:review_id>/', views.delete_review, name='delete_review'),
#     path('change_password/', auth_views.PasswordChangeView.as_view(template_name='accounts/change_password.html'), name='change_password'),
#     path('logout/', auth_views.LogoutView.as_view(), name='logout'),
  
# ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('api/reviews/', views.api_reviews, name='api_reviews'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('add_review/', views.add_review, name='add_review'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset_form.html', email_template_name='accounts/password_reset_email.html', subject_template_name='accounts/password_reset_subject.txt', success_url='/accounts/password_reset/done/'), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html', success_url='/accounts/reset/done/'), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
    path('profile/<str:username>/edit/', views.edit_profile, name='edit_profile'),
    path('edit_review/<int:review_id>/', views.edit_review, name='edit_review'),
    path('api/load_more_reviews/', views.load_more_reviews, name='load_more_reviews'),
    path('api/search_reviews/', views.search_reviews, name='search_reviews'),
    path('company_ratings/', views.company_ratings, name='company_ratings'),
    path('delete_review/<int:review_id>/', views.delete_review, name='delete_review'),
    path('change_password/', auth_views.PasswordChangeView.as_view(template_name='accounts/change_password.html'), name='change_password'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)