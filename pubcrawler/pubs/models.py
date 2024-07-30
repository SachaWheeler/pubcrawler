# from django.db import models
from django.contrib.gis.db import models
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
    # latitude = models.FloatField(db_index=True)
    # longitude = models.FloatField(db_index=True)
    local_authority = models.ForeignKey(LocalAuthority,
            on_delete=models.CASCADE, related_name='pubs', null=True)
    location = models.PointField(geography=True, default=Point(0.0, 0.0))

    @property
    def latitude(self):
        return self.location.y

    @property
    def longitude(self):
        return self.location.x


    def __str__(self):
        return self.name

class Distance(models.Model):
    pub1 = models.ForeignKey(Pub, related_name='distances_from', on_delete=models.CASCADE)
    pub2 = models.ForeignKey(Pub, related_name='distances_to', on_delete=models.CASCADE)
    absolute_distance = models.FloatField()
    walking_distance = models.FloatField()

    class Meta:
        unique_together = (('pub1', 'pub2'),)

    def clean(self):
        if self.pub1 == self.pub2:
            raise ValidationError("A pub cannot have a distance to itself.")

    def __str__(self):
        return f"{self.pub1.name} to {self.pub2.name}"

























