from django.db import models
from django.contrib.gis.db import models as gis_models
from django.core.exceptions import ValidationError
from django.contrib.gis.geos import Point


class LocalAuthority(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Pub(models.Model):
    fas_id = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    address = models.CharField(max_length=255)
    postcode = models.CharField(max_length=20)
    easting = models.IntegerField()
    northing = models.IntegerField()

    local_authority = models.ForeignKey(LocalAuthority,
            on_delete=models.CASCADE, related_name='pubs', null=True)

    # location = models.PointField(geography=True, default=Point(0.0, 0.0))
    geo_location = gis_models.PointField(geography=False, default=Point(0.0, 0.0))

    @property
    def latitude(self):
        return self.geo_location.y

    @property
    def longitude(self):
        return self.geo_location.x


    def __str__(self):
        return self.name

    objects = models.Manager()


class PubDistManager(models.Manager):
    def get_distance(self, point_a, point_b):
        # Ensure the consistent order of the points
        pub1, pub2 = (point_a, point_b) if point_a.id < point_b.id else (point_b, point_a)

        try:
            # Try to retrieve the PubDist object
            distance_record = self.get(pub1=pub1, pub2=pub2)
            return distance_record.walking_distance
        except self.model.DoesNotExist:
            # If no PubDist record is found, return None
            return None


class PubDist(models.Model):
    pub1 = models.ForeignKey(Pub, related_name='distances_from', on_delete=models.CASCADE)
    pub2 = models.ForeignKey(Pub, related_name='distances_to', on_delete=models.CASCADE)
    absolute_distance = models.FloatField()
    walking_distance = models.FloatField()

    class Meta:
        unique_together = ('pub1', 'pub2')
        indexes = [
            models.Index(fields=['pub1', 'pub2']),
        ]

    def clean(self):
        if self.pub1 == self.pub2:
            raise ValidationError("A pub cannot have a distance to itself.")

    def __str__(self):
        return f"{self.pub1.name} to {self.pub2.name}"

    objects = PubDistManager()

























