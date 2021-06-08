from rest_framework.permissions import BasePermission
from django.http import Http404

class IsAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            user = obj.user.pk
        except AttributeError:
            user = obj.scenario.user.pk
        if user == request.user.pk:
            return True
        return False

class CanReadObject(BasePermission):
     def has_object_permission(self, request, view, obj):
         try:
             status = obj.status
             user_id = obj.user.pk
         except AttributeError:
             status = obj.scenario.status
             user_id = obj.scenario.user
         if status == 'published' or \
                 user_id == request.user.pk:
             return True
         raise Http404
