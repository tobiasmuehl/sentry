from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone

from sentry.db.models import BoundedPositiveIntegerField, FlexibleForeignKey, Model


class ReleaseActivity(Model):
    __include_in_export__ = False

    class Type:
        unknown = 0
        created = 1
        deployed = 2
        finished = 3
        issue = 4

    release = FlexibleForeignKey("sentry.Release", db_index=True)
    type = BoundedPositiveIntegerField(
        default=Type.unknown,
        choices=(
            (Type.created, "Created"),
            (Type.deployed, "Deployed"),
            (Type.finished, "Finished"),
            (Type.issue, "Issue"),
        ),
    )
    data = JSONField(default=dict)
    date_added = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = "sentry"
        db_table = "sentry_releaseactivity"
