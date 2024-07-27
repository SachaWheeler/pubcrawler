from django.contrib import admin
from .models import Pub, Distance, LocalAuthority



class PubAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'postcode', 'latitude', 'longitude',
            'local_authority', 'local_authority2')
    search_fields = ('name', 'address', 'postcode', 'local_authority')
    list_filter = ('local_authority',)
    ordering = ('name',)

class DistanceAdmin(admin.ModelAdmin):
    list_display = ('pub1', 'pub2', 'absolute_distance', 'walking_distance')
    search_fields = ('pub1__name', 'pub2__name')
    list_filter = ('absolute_distance', 'walking_distance')

class LocalAuthorityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(Pub, PubAdmin)
admin.site.register(Distance, DistanceAdmin)
admin.site.register(LocalAuthority, LocalAuthorityAdmin)

