from django.contrib import admin
from .models import Pub, Distance, LocalAuthority



class PubAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'postcode', 'latitude', 'longitude',
            'location',
            'local_authority')
    search_fields = ('name', 'address', 'postcode', )
    list_filter = ('local_authority',)
    ordering = ('name',)
    autocomplete_fields = ('local_authority',)

admin.site.register(Pub, PubAdmin)


class DistanceAdmin(admin.ModelAdmin):
    list_display = ('pub1', 'pub2', 'absolute_distance', 'walking_distance')
    search_fields = ('pub1__name', 'pub2__name')
    list_filter = ('pub1__local_authority',)
    autocomplete_fields = ('pub1', 'pub2')

admin.site.register(Distance, DistanceAdmin)


class LocalAuthorityAdmin(admin.ModelAdmin):
    list_display = ('name', 'count')
    search_fields = ('name',)

    def count(self, obj):
        return obj.pubs.count()

admin.site.register(LocalAuthority, LocalAuthorityAdmin)

