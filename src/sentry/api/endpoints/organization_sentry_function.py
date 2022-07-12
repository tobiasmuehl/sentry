from uuid import uuid4

from django.template.defaultfilters import slugify
from rest_framework import serializers
from rest_framework.response import Response

from sentry.api.bases import OrganizationEndpoint
from sentry.api.serializers.rest_framework import CamelSnakeSerializer


class SentryFunctionSerializer(CamelSnakeSerializer):
    name = serializers.CharField()
    author = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class OrganizationSentryFunctionEndpoint(OrganizationEndpoint):
    private = True
    # Creating a new sentry function

    def post(self, request, organization):
        serializer = SentryFunctionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data
        data["slug"] = slugify(data["name"])
        # Currently slug unique within organization
        # In future, may add "global_slug" so users can publish their functions
        data["organization_id"] = organization.id
        data["external_id"] = data["slug"] + "-" + uuid4().hex
        return Response("POSTED!", status=201)

    # def get(self, request, organization):
    #     functions = SentryFunction.objects.filter(organization=organization)
    #     return Response(serialize(list(functions), request.user), status=200)
