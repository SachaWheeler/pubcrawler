from django.core.management.base import BaseCommand
from pubs.models import Pub, Distance
from django.db.models import Q, F
import time
from django.contrib.gis.geos import Point


class Command(BaseCommand):
    help = 'turn lat lon into Points'

    def handle(self, *args, **kwargs):

        distances = Distance.objects.filter(pub1__pk__gt=F('pub2__pk'))
        print(len(distances))

        return
        count = 0
        for distance in distances:
            distance.pub1, distance.pub2 = distance.pub2, distance.pub1
            distance.save()
            count += 1
            # break
            if count%100==0:
                print(f"{count=}")
        print(f"{count=}")
