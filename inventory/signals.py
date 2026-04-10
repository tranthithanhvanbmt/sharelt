import os

from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def ensure_default_admin(sender, **kwargs):
    # Only run for this app's migrate cycle to avoid duplicate work.
    if sender.name != "inventory":
        return

    username = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    password = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
    email = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@shareit.local")

    User = get_user_model()
    user, _ = User.objects.get_or_create(username=username, defaults={"email": email})
    user.email = email
    user.is_staff = True
    user.is_superuser = True
    user.set_password(password)
    user.save()
