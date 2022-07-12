from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response

from sentry.api.base import customer_silo_endpoint
from sentry.api.bases.project import ProjectEndpoint, RelaxedSearchPermission
from sentry.api.exceptions import ResourceDoesNotExist
from sentry.api.serializers import serialize
from sentry.models import SavedSearch, SavedSearchUserDefault


class LimitedSavedSearchSerializer(serializers.Serializer):
    isUserDefault = serializers.BooleanField(required=False)


class SavedSearchSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=128, required=True)
    query = serializers.CharField(required=True)
    isDefault = serializers.BooleanField(required=False)
    isUserDefault = serializers.BooleanField(required=False)


@customer_silo_endpoint
class ProjectSearchDetailsEndpoint(ProjectEndpoint):
    permission_classes = (RelaxedSearchPermission,)

    def get(self, request: Request, project, search_id) -> Response:
        """
        Retrieve a saved search

        Return details on an individual saved search.

            {method} {path}

        """
        try:
            search = SavedSearch.objects.get(project=project, id=search_id)
        except SavedSearch.DoesNotExist:
            raise ResourceDoesNotExist

        return Response(serialize(search, request.user))

    def put(self, request: Request, project, search_id) -> Response:
        """
        Update a saved search

        Update a saved search.

            {method} {path}
            {{
                "name: "Unresolved",
                "query": "is:unresolved",
                "dateSavedSearchd": "2015-05-11T02:23:10Z"
            }}

        """
        try:
            search = SavedSearch.objects.get(project=project, id=search_id)
        except SavedSearch.DoesNotExist:
            raise ResourceDoesNotExist

        has_team_scope = any(
            request.access.has_team_scope(team, "project:write") for team in project.teams.all()
        )
        if has_team_scope:
            serializer = SavedSearchSerializer(data=request.data, partial=True)
        else:
            serializer = LimitedSavedSearchSerializer(data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        result = serializer.validated_data

        kwargs = {}
        if result.get("name"):
            kwargs["name"] = result["name"]
        if result.get("query"):
            kwargs["query"] = result["query"]
        if result.get("isDefault"):
            kwargs["is_default"] = result["isDefault"]

        if kwargs:
            search.update(**kwargs)

        if result.get("isDefault"):
            SavedSearch.objects.filter(project=project).exclude(id=search_id).update(
                is_default=False
            )

        if result.get("isUserDefault"):
            SavedSearchUserDefault.objects.create_or_update(
                user=request.user, project=project, values={"savedsearch": search}
            )

        return Response(serialize(search, request.user))

    def delete(self, request: Request, project, search_id) -> Response:
        """
        Delete a saved search

        Permanently remove a saved search.

            {method} {path}

        """
        try:
            search = SavedSearch.objects.get(project=project, id=search_id)
        except SavedSearch.DoesNotExist:
            raise ResourceDoesNotExist

        is_search_owner = request.user and request.user == search.owner

        if request.access.has_scope("project:write"):
            if not search.owner or is_search_owner:
                search.delete()
                return Response(status=204)
        elif is_search_owner:
            search.delete()
            return Response(status=204)

        return Response(status=403)
