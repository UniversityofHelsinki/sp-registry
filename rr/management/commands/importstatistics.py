"""
Command line script for importing metadata.xml

Usage help: ./manage.py importstatistics -h
"""
import MySQLdb
from datetime import date, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand

from rr.models.serviceprovider import ServiceProvider
from rr.models.statistics import Statistics


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-d', type=int, action='store', dest='number_of_days', default=3,
                            help='How many days in past to import, default 3.')
        parser.add_argument('-t', action='store_true', dest='include_today',
                            help='Include current day')
        parser.add_argument('-p', action='store_true', dest='verbose',
                            help='Print statistics as updated')

    def handle(self, *args, **options):
        number_of_days = options['number_of_days']
        if number_of_days < 1:
            number_of_days = 1
        include_today = options['include_today']
        verbose = options['verbose']
        try:
            host = settings.STATISTICS_DATABASE_HOST
            user = settings.STATISTICS_DATABASE_USER
            password = settings.STATISTICS_DATABASE_PASSWORD
            database = settings.STATISTICS_DATABASE_NAME
            table = settings.STATISTICS_DATABASE_TABLE
        except AttributeError:
            self.stderr.write("Missing database settings")
            exit(1)
        db = MySQLdb.connect(
            host=host,
            user=user,
            passwd=password,
            db=database)
        cursor = db.cursor()
        date_start = (date.today() - timedelta(days=number_of_days)).strftime("%Y-%m-%d") + " 00:00:00"
        if include_today:
            date_end = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d") + " 00:00:00"
        else:
            date_end = (date.today()).strftime("%Y-%m-%d") + " 00:00:00"
        cursor.execute("""SELECT relyingpartyid, DATE(requestTime), count(*), count(distinct principalName) FROM %s
                          WHERE requestTime >= %s and requestTime < %s GROUP BY relyingpartyid,
                          DATE(requestTime);""", (table, date_start, date_end))
        serviceproviders = ServiceProvider.objects.filter(end_at=None)
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            self._save_statistics(row, serviceproviders, verbose)

    def _save_statistics(self, row, serviceproviders, verbose):
        sp = serviceproviders.filter(entity_id=row[0]).first()
        if sp:
            try:
                obj = Statistics.objects.get(sp=sp, date=row[1])
                if obj.logins != row[2] or obj.users != row[3]:
                    obj.logins = row[2]
                    obj.users = row[3]
                    obj.save()
                    status = "UPDATED"
                else:
                    status = "EXISTS"
            except Statistics.DoesNotExist:
                Statistics.objects.create(sp=sp, date=row[1], logins=row[2], users=row[3])
                status = "CREATED"
        else:
            status = "UNKNOWN SP"
        if verbose:
            self.stdout.write("%s;%s;%s;%s;%s" % (status, row[0], row[1], row[2], row[3]))
