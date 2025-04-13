from django.db import models

class CertifiedVet(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email

class User(models.Model):
    id = models.AutoField(primary_key=True)
    is_farmer = models.BooleanField(default=False)
    is_vet = models.BooleanField(default=False)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    location_lat = models.FloatField(null=True, blank=True)
    location_lng = models.FloatField(null=True, blank=True)
    wallet_balance = models.FloatField(default=0.0)

    def __str__(self):
        return self.username

class VeterinarianProfile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vet_profile')
    certification_id = models.CharField(max_length=100)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Vet: {self.user.username}"

class FarmerProfile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    farm_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Farmer: {self.user.username}"

class Appointment(models.Model):
    id = models.AutoField(primary_key=True)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_made')
    vet = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_received')
    date_requested = models.DateTimeField(auto_now_add=True)
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    updated_at = models.DateTimeField(auto_now=True)
    vet_status_updated_at = models.DateTimeField(null=True, blank=True)  # New field for vet's action timestamp
    location_lat = models.FloatField(null=True, blank=True)
    location_lng = models.FloatField(null=True, blank=True)
    farmer_note = models.TextField(blank=True, null=True)
    vet_note = models.TextField(blank=True, null=True)
    time_sent = models.DateTimeField(auto_now_add=True)  # New field to record time when the appointment is created

    def __str__(self):
        return f"Appointment between {self.farmer} and {self.vet} on {self.appointment_date}"

class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification to {self.recipient.username} - {self.message[:30]}"

class Favorite(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    favorite_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'favorite_user')

    def __str__(self):
        return f"{self.user.username} favorited {self.favorite_user.username}"

class Rating(models.Model):
    id = models.AutoField(primary_key=True)
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    vet = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vet_ratings')
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_ratings')
    rating = models.PositiveSmallIntegerField()  # 1 to 5
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating by {self.farmer.username} to {self.vet.username}"

class CoinReward(models.Model):
    COIN_TO_KSH = 25
    MAX_BALANCES = {
        'farmer': 1000000,
        'vet': 3000000
    }

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='coin_reward')
    coins = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.coins} Coins"

    def add_coins(self, amount):
        role = 'farmer' if self.user.is_farmer else 'vet' if self.user.is_vet else None
        max_balance = self.MAX_BALANCES.get(role, 0)
        if self.coins + amount > max_balance:
            raise ValueError(f"Exceeds max balance for {role}.")
        self.coins += amount
        self.save()

    def subtract_coins(self, amount):
        if self.coins >= amount:
            self.coins -= amount
            self.save()
        else:
            raise ValueError("Insufficient coins to withdraw.")

class PlatformCoin(models.Model):
    COIN_TO_KSH = 25  # The conversion rate from coins to Ksh
    MAX_BALANCE = 10000000

    id = models.AutoField(primary_key=True)
    coins = models.IntegerField(default=0)

    def __str__(self):
        balance_in_ksh = self.coins / self.COIN_TO_KSH  # Corrected division instead of multiplication
        return f"Vet Mashinani Platform - {self.coins} Coins (Ksh {balance_in_ksh})"

    def add_coins(self, amount):
        if self.coins + amount > self.MAX_BALANCE:
            raise ValueError("Platform coin limit exceeded.")
        self.coins += amount
        self.save()

    def subtract_coins(self, amount):
        if self.coins >= amount:
            self.coins -= amount
            self.save()
        else:
            raise ValueError("Insufficient platform coin balance.")
