from django.db import models
from django.core.exceptions import ValidationError

class Pub(models.Model):
    fas_id = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    postcode = models.CharField(max_length=20)
    easting = models.IntegerField()
    northing = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    local_authority = models.CharField(max_length=255)

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

