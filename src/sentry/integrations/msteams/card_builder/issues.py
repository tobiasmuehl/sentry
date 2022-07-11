from __future__ import annotations

from typing import Any, Sequence

from sentry.integrations.msteams.card_builder import URL_FORMAT_STR
from sentry.integrations.msteams.utils import ACTION_TYPE
from sentry.integrations.notifications import (
    build_attachment_text,
    build_attachment_title,
    build_footer,
    build_title_link,
    format_actor_option,
    get_timestamp,
)
from sentry.models import Event, Group, GroupStatus, Integration, Project, Rule
from sentry.types.integrations import ExternalProviders

from .base import ActionType, MSTeamsMessageBuilder, TextSize, TextWeight

ASSIGNEE_NOTE = "**Assigned to {assignee}**"

RESOLVE = "Resolve"
RESOLVE_INPUT_ID = "resolveInput"
RESOLVE_INPUT_CHOICES = [
    ("Immediately", "resolved"),
    ("In the current release", "resolved:inCurrentRelease"),
    ("In the next release", "resolved:inNextRelease"),
]

UNRESOLVE = "Unresolve"

IGNORE = "Ignore"
IGNORE_INPUT_ID = "ignoreInput"
IGNORE_INPUT_CHOICES = [
    ("Ignore indefinitely", -1),
    ("1 time", 1),
    ("10 times", 10),
    ("100 times", 100),
    ("1,000 times", 1000),
    ("10,000 times", 10000),
]

STOP_IGNORING = "Stop Ignoring"

ASSIGN = "Assign"
ASSIGN_INPUT_ID = "assignInput"

UNASSIGN = "Unassign"
ME = "ME"


class MSTeamsChoiceInputMessageBuilder(MSTeamsMessageBuilder):
    def __init__(
        self,
        title: str,
        data: Any,
        input_id: str,
        choices: Sequence[str, Any],
        default_choice: Any = None,
    ):
        self.title = title
        self.input_id = input_id
        self.choices = choices
        self.default_choice = default_choice
        self.data = data

    def build(self):
        return self._build(
            title=self.get_text_block(self.title, weight=TextWeight.BOLDER),
            text=self.get_input_choice_set_block(
                id=self.input_id, choices=self.choices, default_choice=self.default_choice
            ),
            actions=self.get_action_block(ActionType.SUBMIT, title=self.title, data=self.data),
        )


class MSTeamsIssueMessageBuilder(MSTeamsMessageBuilder):
    def __init__(self, group: Group, event: Event, rules: Sequence[Rule], integration: Integration):
        self.group = group
        self.event = event
        self.rules = rules
        self.integration = integration

    def build_full_footer(self) -> Any:
        logo = self.get_logo_block(for_footer=True)

        project = Project.objects.get_from_cache(id=self.group.project_id)
        footer = self.get_text_block(
            build_footer(self.group, project, URL_FORMAT_STR, self.rules),
            size=TextSize.SMALL,
            weight=TextWeight.LIGHTER,
        )

        date = get_timestamp(self.group, self.event)
        # date = date_ts.replace(microsecond=0).isoformat()
        date_block = self.get_text_block(
            f"{{{{DATE({date}, SHORT)}}}} at {{{{TIME({date})}}}}",
            size=TextSize.SMALL,
            weight=TextWeight.LIGHTER,
            horizontalAlignment="Center",
        )

        return self.get_column_set_block(
            self.get_column_block(logo),
            self.get_column_block(footer, isSubtle=True, spacing="none"),
            self.get_column_block(date_block),
        )

    def build_assignee_block(self) -> Any | None:
        assignee = self.group.get_assignee()

        if assignee:
            assignee_string = format_actor_option(assignee)
            return self.get_text_block(
                ASSIGNEE_NOTE.format(assignee=assignee_string), size=TextSize.SMALL
            )

    def generate_action_payload(self, action_type: ACTION_TYPE) -> Any:
        rule_ids = map(lambda x: x.id, self.rules)
        # we need nested data or else Teams won't handle the payload correctly
        return {
            "payload": {
                "actionType": action_type,
                "groupId": self.event.group.id,
                "eventId": self.event.event_id,
                "rules": rule_ids,
                "integrationId": self.integration.id,
            }
        }

    def build_resolve_action(self, status: GroupStatus) -> Any:
        if GroupStatus.RESOLVED == status:
            payload_data = self.generate_action_payload(ACTION_TYPE.UNRESOLVE)
            return self.get_action_block(ActionType.SUBMIT, title=UNRESOLVE, data=payload_data)

        payload_data = self.generate_action_payload(ACTION_TYPE.RESOLVE)
        resolve_choices_card = MSTeamsChoiceInputMessageBuilder(
            title=RESOLVE,
            data=payload_data,
            input_id=RESOLVE_INPUT_ID,
            choices=RESOLVE_INPUT_CHOICES,
        ).build()

        return self.get_action_block(ActionType.SHOW_CARD, title=RESOLVE, card=resolve_choices_card)

    def build_ignore_action(self, status: GroupStatus) -> Any:
        if GroupStatus.IGNORED == status:
            payload_data = self.generate_action_payload(ACTION_TYPE.UNRESOLVE)
            return self.get_action_block(ActionType.SUBMIT, title=STOP_IGNORING, data=payload_data)

        payload_data = self.generate_action_payload(ACTION_TYPE.IGNORE)
        ignore_choices_card = MSTeamsChoiceInputMessageBuilder(
            title=IGNORE, data=payload_data, input_id=IGNORE_INPUT_ID, choices=IGNORE_INPUT_CHOICES
        )

        return self.get_action_block(ActionType.SHOW_CARD, title=IGNORE, card=ignore_choices_card)

    def get_teams_choices(self) -> Sequence[str, str]:
        teams = self.group.project.teams.all().order_by("slug")
        return [("Me", ME)] + [(f"#{t.slug}", f"team:{t.id}") for t in teams]

    def build_assign_action(self, status: GroupStatus) -> Any:
        if self.group.get_assignee():
            payload_data = self.generate_action_payload(ACTION_TYPE.UNASSIGN)
            return self.get_action_block(ActionType.SUBMIT, title=UNASSIGN, data=payload_data)

        payload_data = self.generate_action_payload(ACTION_TYPE.ASSIGN)
        teams_choices = self.get_teams_choices()
        assign_choices_card = MSTeamsChoiceInputMessageBuilder(
            title=ASSIGN,
            data=payload_data,
            input_id=ASSIGN_INPUT_ID,
            choices=teams_choices,
            default_choice=ME,
        )

        return self.get_action_block(ActionType.SHOW_CARD, title=ASSIGN, card=assign_choices_card)

    def build_actions(self) -> Any:
        status = self.group.get_status()

        return self.get_container_block(
            self.get_action_set_block(
                self.build_resolve_action(status),
                self.build_ignore_action(status),
                self.build_assign_action(status),
            )
        )

    def build(
        self,
    ):
        title_text = build_attachment_title(self.group or self.event)
        title_link = build_title_link(
            group=self.group,
            event=self.event,
            link_to_event=True,
            issue_details=False,
            notification=None,
            provider=ExternalProviders.MSTEAMS,
        )

        fields = []

        description_text = build_attachment_text(self.group, self.event)
        if description_text:
            fields.append(
                self.get_text_block(
                    description_text, size=TextSize.MEDIUM, weight=TextWeight.BOLDER
                )
            )

        fields.append(self.build_full_footer())

        assignee_block = self.build_assignee_block()
        if assignee_block:
            fields.append(assignee_block)

        fields.append(self.build_actions())

        return self._build(
            title=self.get_text_block(
                URL_FORMAT_STR.format(text=title_text, url=title_link),
                size=TextSize.LARGE,
                weight=TextWeight.BOLDER,
            ),
            fields=fields,
        )
