from django.contrib import admin

import web.models

admin.site.register(web.models.Availability)
admin.site.register(web.models.Board)
admin.site.register(web.models.BoardAction)
admin.site.register(web.models.BoardColumn)
admin.site.register(web.models.BoardPrototype)
admin.site.register(web.models.Log)
admin.site.register(web.models.Profile)
admin.site.register(web.models.Sprint)
admin.site.register(web.models.Story)
admin.site.register(web.models.StoryAction)
admin.site.register(web.models.Task)