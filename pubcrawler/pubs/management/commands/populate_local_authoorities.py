from django.core.management.base import BaseCommand
from pubs.models import Pub, LocalAuthority

class Command(BaseCommand):
    help = 'Populate LocalAuthority model with unique local authorities from Pub model'

    def handle(self, *args, **kwargs):
        # for pub in Pub.objects.all():
        for pub in Pub.objects.filter(local_authority2__isnull=True):
            la, _ = LocalAuthority.objects.get_or_create(name=pub.local_authority)
            pub.local_authority2 = la
            pub.local_authority = ""
            pub.save()
            print(pub)
            # print(pub.local_authority, pub.local_authority2)
            # break
        self.stdout.write(self.style.SUCCESS('Successfully populated LocalAuthority model'))

