from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import make_password


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email,  password, **extra_fields):

        values = [email, ]
        field_value_map = dict(zip(self.model.REQUIRED_FIELDS, values))

        for field_name, value in field_value_map.items():
            if not value:
                raise ValueError('The {} value must be set'.format(field_name))

        email = self.normalize_email(email)

        user = self.model(
            email=email,

            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email,  password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email,  password, **extra_fields)

    def create_superuser(self, email,  password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email,  password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    company_name = models.CharField(max_length=255)
    slug = models.CharField(max_length=305, null=True, blank=True)
    credit = models.IntegerField(default=10, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return f'{self.email}'


class Poll(models.Model):
    organizer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    month = models.CharField(max_length=20)
    title = models.CharField(max_length=250, null=True, unique=True)
    vote_start = models.DateField(null=True)
    vote_end = models.DateField(null=True)
    nominees = models.JSONField(null=True, default=list)

    def __str__(self):
        return self.organizer.company_name + " - " + str(self.title)


class Leaderboard(models.Model):
    organizer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    month = models.CharField(max_length=20, null=True)
    nominees = models.JSONField(null=True, default=list)

    def __str__(self):
        return self.organizer.company_name + " - " + str(self.month)


class Employee(models.Model):
    employee_name = models.CharField(max_length=200)
    # nominee_note = models.TextField(null=True, blank=True)
    employee_position = models.TextField(null=True, blank=True)
    employer = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True)
    # vote_count = models.IntegerField(null=True, blank=True, default=0)

    def __str__(self):

        return self.employee_name + " employed by " + self.employer.company_name


# class Vote(models.Model):
#     poll = models.ForeignKey(
#         Poll, on_delete=models.CASCADE, null=True, blank=True)
#     choice = models.ForeignKey(Employee, on_delete=models.CASCADE)
#     vote_count = models.IntegerField(null=True, blank=True, default=0)

#     def __str__(self):
#         return self.poll.organizer.company_name
