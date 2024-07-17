from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from .models import Review, Profile, answer_coin, Transaction, Company
from .models import Review, Profile, answer_coin, TransactionModel, Company
from .forms import ReviewForm, ProfileUpdateForm
from django.contrib.auth.models import User  
from django.core.exceptions import PermissionDenied  
from django.http import JsonResponse
from .models import Review
from django.db.models import Q
from django.contrib.auth import views as auth_views
from django.views.i18n import set_language
from django.shortcuts import redirect

def my_set_language(request):
    response = set_language(request)
    language = request.GET.get('language', None)
    if language:
        return redirect(f'/{language}/') # Перенаправление на URL с префиксом языка
    return response
##
def calculate_reward(user, review):
    R_user = user.profile.rating
    L = len(review.text)
    R_company = review.company.rating
    S_user = review.rating
    K_score = 0.5 if S_user in [1, 2, 9, 10] else 1.5
    B_reviews = 50  # This can be adjusted based on the number of reviews

    reward = (R_user * L * R_company * K_score) + B_reviews
    return reward


# @login_required
# def edit_review(request, review_id):
#     review = get_object_or_404(Review, id=review_id)
#     if review.author != request.user:
#         raise PermissionDenied

#     if request.method == 'POST':
#         form = ReviewForm(request.POST, instance=review)
#         if form.is_valid():
#             form.save()
#             return redirect('profile', username=request.user.username)
#     else:
#         form = ReviewForm(instance=review)
#     return render(request, 'edit_review.html', {'form': form})

def company_ratings(request):
    #companies = Company.objects.all()
    companies = Company.objects.all().order_by('-rating')
    return render(request, 'company_ratings.html', {'companies': companies})


# def load_more_reviews(request):
#     offset = int(request.GET.get('offset', 0))
#     limit = int(request.GET.get('limit', 8))
#     reviews = Review.objects.all()[offset: offset + limit]
#     reviews_data = [{
#         'author': 'Анонимно' if review.is_anonymous else review.author.username,
#         'text': review.text,
#         'service': review.service,
#         'rating': review.rating  # Добавляем рейтинг
#     } for review in reviews]
#     return JsonResponse({'reviews': reviews_data})

# def search_reviews(request):
#     query = request.GET.get('query', '')
#     reviews = Review.objects.filter(service__icontains=query)[:8]  # Ограничиваем количество результатов
#     reviews_data = [{
#         'author': 'Анонимно' if review.is_anonymous else review.author.username,
#         'text': review.text,
#         'service': review.service,
#         'rating': review.rating  # Добавляем рейтинг
#     } for review in reviews]
#     return JsonResponse({'reviews': reviews_data})

def load_more_reviews(request):
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 8))
    reviews = Review.objects.all().order_by('-timestamp')[offset: offset + limit]
    reviews_data = [{
        'author': 'Анонимно' if review.is_anonymous else review.author.username,
        'text': review.text,
        'service': review.service,
        'rating': review.rating,  # Добавляем рейтинг
        'image': review.image.url if review.image else None
        #'image': review.image
    } for review in reviews]
    return JsonResponse({'reviews': reviews_data})

def search_reviews(request):
    query = request.GET.get('query', '')
    reviews = Review.objects.filter(service__icontains=query).order_by('-timestamp')[:8]  # Ограничиваем количество результатов
    reviews_data = [{
        'author': 'Анонимно' if review.is_anonymous else review.author.username,
        'text': review.text,
        'service': review.service,
        'rating': review.rating,  # Добавляем рейтинг
        'image': review.image.url if review.image else None
        #'image': review.image
    } for review in reviews]
    return JsonResponse({'reviews': reviews_data})

def api_reviews(request):
    page = int(request.GET.get('page', 1))
    reviews_per_page = 8
    start = (page - 1) * reviews_per_page
    end = start + reviews_per_page
    reviews = Review.objects.all()[start:end]
    reviews_data = [{
        'author': 'Анонимно' if review.is_anonymous else review.author.username,
        'text': review.text,
        'service': review.service
    } for review in reviews]
    return JsonResponse({'reviews': reviews_data})

def index(request):
    reviews = Review.objects.all().order_by('-timestamp')
    context = {'reviews': reviews}
    return render(request, 'index.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('profile', username=request.user.username)
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


from .models import Review, Profile, answer_coin, TransactionModel, Company, Transaction
from datetime import timedelta
from django.utils import timezone
from django.contrib import messages

# @login_required
# def add_review(request):
#     if request.method == 'POST':
#         form = ReviewForm(request.POST)
#         if form.is_valid():
#             service = form.cleaned_data['service']
#             # Проверка на существование отзыва за последние 15 дней
#             recent_review = Review.objects.filter(
#                 author=request.user,
#                 service=service,
#                 timestamp__gte=timezone.now() - timedelta(days=15)
#             ).exists()

#             if recent_review:
#                 messages.error(request, 'You can only leave one review for the same service every 15 days.')
#                 return redirect('add_review')

#             review = form.save(commit=False)
#             review.author = request.user
#             review.save()

#             reward = calculate_reward(request.user, review)
#             request.user.profile.balance += reward
#             request.user.profile.save()

#             # Сохранение транзакции в базе данных
#             transaction_model = TransactionModel(sender="Система", recipient=request.user.username, amount=reward)
#             transaction_model.save()

#             # Конвертация TransactionModel в Transaction
#             transaction = transaction_model.to_transaction()
#             answer_coin.add_transaction(transaction)
#             mined_block = answer_coin.mine_block(miner_address="Майнер")
#             if answer_coin.add_block(mined_block):
#                 print(f"Блок {mined_block.index} добавлен в блокчейн!")

#                 # Добавляем бонус за каждый 10-й отзыв
#                 if len(answer_coin.chain) % 10 == 0:
#                     bonus_transaction_model = TransactionModel(sender="Система", recipient="admin", amount=100000)
#                     bonus_transaction_model.save()
#                     bonus_transaction = bonus_transaction_model.to_transaction()
#                     answer_coin.add_transaction(bonus_transaction)
#                     mined_block = answer_coin.mine_block(miner_address="Майнер")
#                     if answer_coin.add_block(mined_block):
#                         print(f"Бонусный блок {mined_block.index} добавлен в блокчейн!")
#                         admin_user = User.objects.get(username="admin")
#                         admin_user.profile.bonus_balance += 100000
#                         admin_user.profile.save()

#             return redirect('profile', username=request.user.username)
#     else:
#         form = ReviewForm()
#     return render(request, 'add_review.html', {'form': form})

# @login_required
# def add_review(request):
#     if request.method == 'POST':
#         form = ReviewForm(request.POST, request.FILES)
#         if form.is_valid():
#             service = form.cleaned_data['service']
#             # Проверка на существование отзыва за последние 15 дней
#             recent_review = Review.objects.filter(
#                 author=request.user,
#                 service=service,
#                 timestamp__gte=timezone.now() - timedelta(days=15)
#             ).exists()

#             if recent_review:
#                 messages.error(request, 'You can only leave one review for the same service every 15 days.')
#                 return redirect('add_review')

#             review = form.save(commit=False)
#             review.author = request.user
#             review.save()

#             reward = calculate_reward(request.user, review)
#             request.user.profile.balance += reward
#             request.user.profile.save()

#             # Сохранение транзакции в базе данных
#             transaction_model = TransactionModel(sender="Система", recipient=request.user.username, amount=reward)
#             transaction_model.save()

#             # Конвертация TransactionModel в Transaction
#             transaction = transaction_model.to_transaction()
#             answer_coin.add_transaction(transaction)
#             mined_block = answer_coin.mine_block(miner_address="Майнер")
#             if answer_coin.add_block(mined_block):
#                 print(f"Блок {mined_block.index} добавлен в блокчейн!")

#                 # Добавляем бонус за каждый 10-й отзыв
#                 if len(answer_coin.chain) % 10 == 0:
#                     bonus_transaction_model = TransactionModel(sender="Система", recipient="admin", amount=100000)
#                     bonus_transaction_model.save()
#                     bonus_transaction = bonus_transaction_model.to_transaction()
#                     answer_coin.add_transaction(bonus_transaction)
#                     mined_block = answer_coin.mine_block(miner_address="Майнер")
#                     if answer_coin.add_block(mined_block):
#                         print(f"Бонусный блок {mined_block.index} добавлен в блокчейн!")
#                         admin_user = User.objects.get(username="admin")
#                         admin_user.profile.bonus_balance += 100000
#                         admin_user.profile.save()

#             return redirect('profile', username=request.user.username)
#     else:
#         form = ReviewForm()
#     return render(request, 'add_review.html', {'form': form})
from django.core.exceptions import ValidationError

@login_required
def add_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                service = form.cleaned_data['service']
                # Проверка на существование отзыва за последние 15 дней
                recent_review = Review.objects.filter(
                    author=request.user,
                    service=service,
                    timestamp__gte=timezone.now() - timedelta(days=15)
                ).exists()

                if recent_review:
                    messages.error(request, 'You can only leave one review for the same service every 15 days.')
                    return redirect('add_review')

                review = form.save(commit=False)
                review.author = request.user
                review.save()

                reward = calculate_reward(request.user, review)
                request.user.profile.balance += reward
                request.user.profile.save()

                # Сохранение транзакции в базе данных
                transaction_model = TransactionModel(sender="Система", recipient=request.user.username, amount=reward)
                transaction_model.save()

                # Конвертация TransactionModel в Transaction
                transaction = transaction_model.to_transaction()
                answer_coin.add_transaction(transaction)
                mined_block = answer_coin.mine_block(miner_address="Майнер")
                if answer_coin.add_block(mined_block):
                    print(f"Блок {mined_block.index} добавлен в блокчейн!")

                    # Добавляем бонус за каждый 10-й отзыв
                    if len(answer_coin.chain) % 10 == 0:
                        bonus_transaction_model = TransactionModel(sender="Система", recipient="admin", amount=100000)
                        bonus_transaction_model.save()
                        bonus_transaction = bonus_transaction_model.to_transaction()
                        answer_coin.add_transaction(bonus_transaction)
                        mined_block = answer_coin.mine_block(miner_address="Майнер")
                        if answer_coin.add_block(mined_block):
                            print(f"Бонусный блок {mined_block.index} добавлен в блокчейн!")
                            admin_user = User.objects.get(username="admin")
                            admin_user.profile.bonus_balance += 100000
                            admin_user.profile.save()

                return redirect('profile', username=request.user.username)
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = ReviewForm()
    return render(request, 'add_review.html', {'form': form})

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if review.author != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()
            return redirect('profile', username=request.user.username)
    else:
        form = ReviewForm(instance=review)
    return render(request, 'edit_review.html', {'form': form})

def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(email=data)
            if associated_users.exists():
                for user in associated_users:
                    subject = "Запрос на сброс пароля"
                    email_template_name = "accounts/password_reset_email.txt"
                    c = {
                        "email": user.email,
                        'domain': get_current_site(request).domain,
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'https' if request.is_secure() else 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect ("/accounts/password_reset/done/")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="accounts/password_reset.html", context={"password_reset_form":password_reset_form})

@login_required
def edit_profile(request, username):
    user = get_object_or_404(User, username=username)
    if request.user != user and not request.user.is_superuser:
        raise PermissionDenied
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile', username=username)
    else:
        form = ProfileUpdateForm(instance=user)
    return render(request, 'edit_profile.html', {'form': form})

@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    if request.user != user and not request.user.is_superuser:
        raise PermissionDenied
    reviews = Review.objects.filter(author=user).order_by('-timestamp')
    return render(request, 'profile.html', {'user': user, 'reviews': reviews})

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if review.author == request.user:
        review.delete()
        messages.success(request, 'Review deleted successfully.')
    else:
        messages.error(request, 'You do not have permission to delete this review.')
    return redirect('profile', username=request.user.username)
