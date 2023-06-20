"""
Update valid_for for testusers

Usage: ./manage.py updatetestusers
"""

from django.core.management.base import BaseCommand

from rr.models.testuser import TestUser


class Command(BaseCommand):
    def handle(self, *args, **options):
        test_users = TestUser.objects.filter(end_at=None)
        for test_user in test_users:
            test_user.valid_for.add(test_user.sp)
            print("Update test user: " + test_user.username)
