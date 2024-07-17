from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import hashlib
import datetime
import json

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.difficulty = 4
        self.mining_reward = 10000  # Обновлено для 10000 монет
        self.bonus_reward = 100000  # Бонус за каждый 10-й блок
        self.admin_address = "admin"  # Адрес администратора

    def create_genesis_block(self):
        return Block(0, "0", [], datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def get_last_block(self):
        return self.chain[-1]

    def add_block(self, block):
        if self.is_valid_block(block, self.get_last_block()):
            self.chain.append(block)
            return True
        return False

    def is_valid_block(self, block, previous_block):
        if previous_block.hash != block.previous_hash:
            return False
        if block.index != previous_block.index + 1:
            return False
        if not self.is_valid_proof(block):
            return False
        return True

    def is_valid_proof(self, block):
        return block.hash.startswith("0" * self.difficulty)

    def mine_block(self, miner_address):
        block = Block(
            index=len(self.chain),
            previous_hash=self.get_last_block().hash,
            transactions=self.pending_transactions,
            timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        self.pending_transactions.append(Transaction(None, miner_address, self.mining_reward))
        
        # Добавляем бонус каждые 10 блоков
        if len(self.chain) % 10 == 0:
            self.pending_transactions.append(Transaction(None, self.admin_address, self.bonus_reward))

        block.nonce = 0
        while not self.is_valid_proof(block):
            block.nonce += 1
            block.hash = block.calculate_hash()
        self.pending_transactions = []  # Очистка списка транзакций после майнинга блока
        return block

    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)

class Transaction:
    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        data = f"{self.sender}{self.recipient}{self.amount}{self.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()

    def to_dict(self):
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'timestamp': self.timestamp,
            'hash': self.hash
        }

class Block:
    def __init__(self, index, previous_hash, transactions, timestamp, nonce=0):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.timestamp = timestamp
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        transactions_dict = [t.to_dict() for t in self.transactions]
        block_string = json.dumps({
            'index': self.index,
            'previous_hash': self.previous_hash,
            'transactions': transactions_dict,
            'timestamp': self.timestamp,
            'nonce': self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self):
        return {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'transactions': [t.to_dict() for t in self.transactions],
            'timestamp': self.timestamp,
            'nonce': self.nonce,
            'hash': self.hash
        }


answer_coin = Blockchain()

class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)
    rating = models.FloatField(default=1.0)

    def update_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            self.rating = sum(review.rating for review in reviews) / reviews.count()
            self.save()

    def __str__(self):
        return self.name
    


# class Review(models.Model):
#     service = models.CharField(max_length=100)
#     topic = models.CharField(max_length=200)
#     text = models.TextField()
#     author = models.ForeignKey(User, on_delete=models.CASCADE)
#     timestamp = models.DateTimeField(auto_now_add=True)
#     is_anonymous = models.BooleanField(default=False)
#     rating = models.IntegerField(default=1)  # Рейтинг от 1 до 10
#     company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)

#     def save(self, *args, **kwargs):
#         # Создаем или обновляем компанию
#         company, created = Company.objects.get_or_create(name=self.service)
#         self.company = company
#         super().save(*args, **kwargs)
#         company.update_rating()

#     def __str__(self):
#         return f"{self.topic} by {self.author.username if not self.is_anonymous else 'Anonymous'}"
class Review(models.Model):
    service = models.CharField(max_length=100)
    topic = models.CharField(max_length=200)
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_anonymous = models.BooleanField(default=False)
    rating = models.IntegerField(default=1)  # Рейтинг от 1 до 10
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    image = models.ImageField(upload_to='review_images/', null=True, blank=True)  # Поле для изображения
    video = models.FileField(upload_to='review_videos/', null=True, blank=True)  # Поле для видео

    def save(self, *args, **kwargs):
        # Создаем или обновляем компанию
        company, created = Company.objects.get_or_create(name=self.service)
        self.company = company
        super().save(*args, **kwargs)
        company.update_rating()

    def __str__(self):
        return f"{self.topic} by {self.author.username if not self.is_anonymous else 'Anonymous'}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.FloatField(default=0.0)
    rating = models.FloatField(default=1.0)  # Рейтинг пользователя
    bonus_balance = models.FloatField(default=0.0)  # Бонусный баланс

    def __str__(self):
        return f"{self.user.username} Profile"
    

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        instance.profile.balance = 1.0
        instance.profile.save()
        transaction = Transaction(sender="Система", recipient=instance.username, amount=1.0)
        answer_coin.add_transaction(transaction)
        mined_block = answer_coin.mine_block(miner_address="Майнер")
        if answer_coin.add_block(mined_block):
            print(f"Блок {mined_block.index} добавлен в блокчейн!")

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

    
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError

class TransactionModel(models.Model):
    sender = models.CharField(max_length=100)
    recipient = models.CharField(max_length=100)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    hash = models.CharField(max_length=64, blank=True)

    def save(self, *args, **kwargs):
        if not self.hash:
            self.hash = self.calculate_hash()
        self.process_transaction()
        super().save(*args, **kwargs)

    def calculate_hash(self):
        data = f"{self.sender}{self.recipient}{self.amount}{self.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()

    def to_transaction(self):
        return Transaction(
            sender=self.sender,
            recipient=self.recipient,
            amount=self.amount
        )

    def process_transaction(self):
        if self.sender != "Система":
            try:
                sender_user = User.objects.get(username=self.sender)
                if self.sender == "admin":
                    if sender_user.profile.bonus_balance < self.amount:
                        raise ValidationError("Insufficient bonus balance")
                    sender_user.profile.bonus_balance -= self.amount
                else:
                    if sender_user.profile.balance < self.amount:
                        raise ValidationError("Insufficient balance")
                    sender_user.profile.balance -= self.amount
                sender_user.profile.save()
            except ObjectDoesNotExist:
                pass

        if self.recipient != "Система":
            try:
                recipient_user = User.objects.get(username=self.recipient)
                recipient_user.profile.balance += self.amount
                recipient_user.profile.save()
            except ObjectDoesNotExist:
                pass

    def __str__(self):
        return f"{self.sender} -> {self.recipient}: {self.amount}"