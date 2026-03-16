from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):

    def create_user(self, email, unique_id, password=None):
        if not email:
            raise ValueError("Email is required")
        if not unique_id:
            raise ValueError("Unique ID is required")

        email = self.normalize_email(email)
        user = self.model(email=email, unique_id=unique_id)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, unique_id, password):
        user = self.create_user(email, unique_id, password)
        user.role = 'SUPER_ADMIN'
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
