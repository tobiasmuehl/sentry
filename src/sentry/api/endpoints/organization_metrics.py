from rest_framework.exceptions import ParseError
from rest_framework.request import Request
from rest_framework.response import Response

from sentry import features
from sentry.api.bases.organization import OrganizationEndpoint
from sentry.api.exceptions import ResourceDoesNotExist
from sentry.api.paginator import GenericOffsetPaginator
from sentry.api.utils import InvalidParams
from sentry.snuba.metrics import (
    QueryDefinition,
    get_metrics,
    get_series,
    get_single_metric_info,
    get_tag_values,
    get_tags,
)
from sentry.snuba.metrics.utils import DerivedMetricException, DerivedMetricParseException
from sentry.snuba.sessions_v2 import InvalidField
from sentry.utils.cursors import Cursor, CursorResult


class OrganizationMetricsEndpoint(OrganizationEndpoint):
    """Get metric name, available operations and the metric unit"""

    def get(self, request: Request, organization) -> Response:
        if not features.has("organizations:metrics", organization, actor=request.user):
            return Response(status=404)

        projects = self.get_projects(request, organization)
<<<<<<< HEAD
        metrics = get_metrics(projects, use_case_id=self.get_use_case_id(request))
||||||| parent of eb68d99586 (add useCase optional query param)
        metrics = get_metrics(projects, UseCaseKey.RELEASE_HEALTH)
=======
        use_case_id = UseCaseKey.from_str(request.GET.get("useCase", "releath-health"))
        metrics = get_metrics(projects, use_case_id)
>>>>>>> eb68d99586 (add useCase optional query param)
        # TODO: replace this with a serializer so that if the structure of MetricMeta changes the response of this
        # endpoint does not
        for metric in metrics:
            del metric["metric_id"]
        return Response(metrics, status=200)


class OrganizationMetricDetailsEndpoint(OrganizationEndpoint):
    """Get metric name, available operations, metric unit and available tags"""

    def get(self, request: Request, organization, metric_name) -> Response:
        if not features.has("organizations:metrics", organization, actor=request.user):
            return Response(status=404)

        projects = self.get_projects(request, organization)
        use_case_id = UseCaseKey.from_str(request.GET.get("useCase", "releath-health"))
        try:
<<<<<<< HEAD
            metric = get_single_metric_info(
                projects, metric_name, use_case_id=self.get_use_case_id(request)
            )
||||||| parent of eb68d99586 (add useCase optional query param)
            metric = get_single_metric_info(projects, metric_name, UseCaseKey.RELEASE_HEALTH)
=======
            metric = get_single_metric_info(projects, metric_name, use_case_id)
>>>>>>> eb68d99586 (add useCase optional query param)
        except InvalidParams as e:
            raise ResourceDoesNotExist(e)
        except (InvalidField, DerivedMetricParseException) as exc:
            raise ParseError(detail=str(exc))

        return Response(metric, status=200)


class OrganizationMetricsTagsEndpoint(OrganizationEndpoint):
    """Get list of tag names for this project

    If the ``metric`` query param is provided, only tags for a certain metric
    are provided.

    If the ``metric`` query param is provided more than once, the *intersection*
    of available tags is used.

    """

    def get(self, request: Request, organization) -> Response:

        if not features.has("organizations:metrics", organization, actor=request.user):
            return Response(status=404)

        metric_names = request.GET.getlist("metric") or None
        projects = self.get_projects(request, organization)
        use_case_id = UseCaseKey.from_str(request.GET.get("useCase", "releath-health"))
        try:
<<<<<<< HEAD
            tags = get_tags(projects, metric_names, use_case_id=self.get_use_case_id(request))
||||||| parent of eb68d99586 (add useCase optional query param)
            tags = get_tags(projects, metric_names, UseCaseKey.RELEASE_HEALTH)
=======
            tags = get_tags(projects, metric_names, use_case_id)
>>>>>>> eb68d99586 (add useCase optional query param)
        except (InvalidParams, DerivedMetricParseException) as exc:
            raise (ParseError(detail=str(exc)))

        return Response(tags, status=200)


class OrganizationMetricsTagDetailsEndpoint(OrganizationEndpoint):
    """Get all existing tag values for a metric"""

    def get(self, request: Request, organization, tag_name) -> Response:

        if not features.has("organizations:metrics", organization, actor=request.user):
            return Response(status=404)

        metric_names = request.GET.getlist("metric") or None

        projects = self.get_projects(request, organization)
        use_case_id = UseCaseKey.from_str(request.GET.get("useCase", "releath-health"))
        try:
<<<<<<< HEAD
            tag_values = get_tag_values(
                projects, tag_name, metric_names, use_case_id=self.get_use_case_id(request)
            )
||||||| parent of eb68d99586 (add useCase optional query param)
            tag_values = get_tag_values(projects, tag_name, metric_names, UseCaseKey.RELEASE_HEALTH)
=======
            tag_values = get_tag_values(projects, tag_name, metric_names, use_case_id)
>>>>>>> eb68d99586 (add useCase optional query param)
        except (InvalidParams, DerivedMetricParseException) as exc:
            msg = str(exc)
            # TODO: Use separate error type once we have real data
            if "Unknown tag" in msg:
                raise ResourceDoesNotExist(f"tag '{tag_name}'")
            else:
                raise ParseError(msg)

        return Response(tag_values, status=200)


class OrganizationMetricsDataEndpoint(OrganizationEndpoint):
    """Get the time series data for one or more metrics.

    The data can be filtered and grouped by tags.
    Based on `OrganizationSessionsEndpoint`.
    """

    default_per_page = 50

    def get(self, request: Request, organization) -> Response:
        if not (
            features.has("organizations:metrics", organization, actor=request.user)
            or features.has("organizations:dashboards-releases", organization, actor=request.user)
        ):
            return Response(status=404)

        projects = self.get_projects(request, organization)

        def data_fn(offset: int, limit: int):
            try:
                query = QueryDefinition(
                    projects, request.GET, paginator_kwargs={"limit": limit, "offset": offset}
                )
                data = get_series(
<<<<<<< HEAD
                    projects, query.to_metrics_query(), use_case_id=self.get_use_case_id(request)
||||||| parent of eb68d99586 (add useCase optional query param)
                    projects, query.to_metrics_query(), use_case_id=UseCaseKey.RELEASE_HEALTH
=======
                    projects,
                    query.to_metrics_query(),
                    use_case_id=UseCaseKey.from_str(request.GET.get("useCase", "releath-health")),
>>>>>>> eb68d99586 (add useCase optional query param)
                )
                data["query"] = query.query
            except (
                InvalidParams,
                DerivedMetricException,
            ) as exc:
                raise (ParseError(detail=str(exc)))
            return data

        return self.paginate(
            request,
            paginator=MetricsDataSeriesPaginator(data_fn=data_fn),
            default_per_page=self.default_per_page,
            max_per_page=100,
        )


class MetricsDataSeriesPaginator(GenericOffsetPaginator):
    def get_result(self, limit, cursor=None):
        assert limit > 0
        offset = cursor.offset if cursor is not None else 0
        data = self.data_fn(offset=offset, limit=limit + 1)

        if isinstance(data.get("groups"), list):
            has_more = len(data["groups"]) == limit + 1
            if has_more:
                data["groups"].pop()
        else:
            raise NotImplementedError

        return CursorResult(
            data,
            prev=Cursor(0, max(0, offset - limit), True, offset > 0),
            next=Cursor(0, max(0, offset + limit), False, has_more),
        )
