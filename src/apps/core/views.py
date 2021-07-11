from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.scenario.api.serializers import TagSerializer
from .permissions import IsAuthor, CanReadObject


# generic tag views
"""
I have to acces through the scenario 
tag manager, since I can not save it 
without checking the permissions 

This:
    serializer.validated_data['scenario']

Can not be done since the scenario id is 
not posted with the tag unlike the other models.
We will use the slug to get both the scenario and the tags to 
validate and filter the data.
I hope it is not too confusing...
And I (of course) have to return the data manually.
"""


class TagDeleteView(generics.GenericAPIView):
    queryset = ''
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated, IsAuthor]
    lookup_field = "slug"

    @action(detail=True, methods=["delete"])
    def delete(self, request, *args, **kwargs):
        target = self.get_object()
        tag_id = kwargs["pk"]
        tag = target.tags.get(pk=tag_id)
        target.tags.remove(tag)
        return Response(status=204)


class TagCreateView(generics.CreateAPIView):
    queryset = ''
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated, IsAuthor]
    lookup_field = "slug"

    def create(self, request, *args, **kwargs):
        if "name" in request.data:
            target = self.get_object()
            tag_name = request.data["name"]
            target.tags.add(request.data["name"])
            new_tag = target.tags.get(name=tag_name)
            response_json = {
                "id": new_tag.id,
                "slug": new_tag.slug,
                "name": new_tag.name,
            }
            return Response(response_json, status=201)
        return Response(status=400)

