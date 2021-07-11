from rest_framework.permissions import BasePermission
from django.http import Http404
from django.db import models


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
    def check_parents(self, request, folder):
        # meant to check if aany folder parent is public
        # so children become available too. This also counts
        # for private scenarios, however, only the preview will be
        # visible (good for a teaser).
        try:
            while True:
                folder = folder.parents.get(user=request.user)
                if folder.status == "published":
                    return True
        except models.DoesNotExist:
            return False

    def has_object_permission(self, request, view, obj):
        try:
            status = obj.status
            user_id = obj.user.pk
        except AttributeError:
            status = obj.scenario.status
            user_id = obj.scenario.user
        if (
            status == "published"
            or user_id == request.user.pk
            or self.check_parents(request, obj)
        ):
            return True
        raise Http404
