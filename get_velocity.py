#!/usr/bin/env python3

# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT

from collections import OrderedDict
from datetime import timedelta, datetime
from time import sleep
from typing import List, Tuple, Optional

import click
from github import GithubException
from ogr import GithubService
from ogr.abstract import IssueStatus
from ogr.services.github import GithubProject, GithubIssue


def get_closed_issues(
    project: GithubProject, tries=10, interval=10
) -> List[GithubIssue]:
    last_ex: Optional[GithubException] = None
    for _ in range(tries):
        try:
            return project.get_issue_list(status=IssueStatus.closed)  # type: ignore
        except GithubException as ex:
            last_ex = ex
            click.echo("Retrying because of the API limit.")
            sleep(interval)
    else:
        raise last_ex  # type: ignore


def is_counted(issue: GithubIssue) -> bool:
    if issue._raw_issue.state_reason == "not_planned":
        return False
    if not issue.assignees:
        return False
    return True


def get_week_representation(date_time) -> str:
    year = date_time.year
    week = date_time.isocalendar()[1]
    week_str = f"{year}-{week:02d}"
    return week_str


def get_issue_value(
    issue: GithubIssue,
    labels: Optional[List[Tuple[str, int]]] = None,
    value_without_label=0,
):
    if not labels:
        return 1

    issue_labels = [label.name for label in issue.labels]
    value: Optional[int] = None
    for label_name, label_value in labels:
        if label_name in issue_labels:
            value = label_value

    if value is not None:
        return value

    click.echo(f"label not set: {issue.url}")
    return value_without_label


def get_closed_issues_per_week(
    projects,
    service,
    interval=0,
    labels: Optional[List[Tuple[str, int]]] = None,
    value_without_label=0,
    since: Optional[datetime] = None,
):
    since = since or (datetime.now() - timedelta(days=365 * 3))
    week_numbers = {}
    for week in get_week_numbers_since(since):
        week_numbers[week] = 0
    click.echo(week_numbers)
    for project in projects:
        namespace, project_name = project.split("/")
        click.echo(f"{namespace}/{project_name}")
        gh_project = service.get_project(namespace=namespace, repo=project_name)
        for issue in get_closed_issues(gh_project, interval=interval):
            if not is_counted(issue):
                continue

            week_str = get_week_representation(issue._raw_issue.closed_at)
            value = get_issue_value(
                issue, labels, value_without_label=value_without_label
            )

            if week_str in week_numbers:
                week_numbers[week_str] += value

    result = OrderedDict(sorted(week_numbers.items()))
    for week, count in result.items():
        click.echo(f"{week};{count}")
    return week_numbers


def get_week_numbers_since(since: datetime) -> List[str]:
    delta = timedelta(days=7)

    current_date = datetime.now()
    week_numbers = []
    while current_date > since:
        week_numbers.append(get_week_representation(current_date))
        current_date -= delta
    return week_numbers


DEFAULT_PROJECTS = [
    "packit/ogr",
    "packit/requre",
    "packit/specfile",
    "packit/packit",
    "packit/research",
    "packit/weekly-roles",
    "packit/tokman",
    "packit/wait-for-copr",
    "packit/sandcastle",
    "packit/packit-service-zuul",
    "packit/packit-service-fedmsg",
    "packit/packit-service",
    "packit/dist-git-to-source-git",
    "packit/deployment",
    "packit/hardly",
    "packit/dashboard",
    "packit/packit.dev",
    "packit/private",
    "packit/packit-service-centosmsg",
]


@click.command(
    help="Get the weekly number of issues closed",
)
@click.option(
    "-t",
    "--token",
    type=click.STRING,
    help="GitHub token",
)
@click.option(
    "-s",
    "--since",
    type=click.DateTime(),
    help="Datetime to start the statistic.",
)
@click.option(
    "-l",
    "--label",
    nargs=2,
    type=click.Tuple([str, int]),
    multiple=True,
    help="Set values to labeled issues.\n"
    "Later definition has priority.\n"
    "Other issues not counted if set.\n"
    "All returns 1 when not set.\n",
)
@click.option(
    "--value-without-label",
    type=click.INT,
    default=0,
    help="When label option is used,\n"
    "this value is used for issues without particular label.",
)
@click.argument(
    "project",
    type=click.STRING,
    nargs=-1,
)
def velocity(token, label, value_without_label, project):
    """
    Use NAMESPACE/PROJECT as arguments to get issues from.

    E.g. get_velocity --value-without-label 3 \
         -t ghp_* -l complexity/easy-fix 2 \
         -l complexity/epic 0 \
         -l complexity/single-task 5 \
         packit/packit packit/ogr


    Multiple can be provided.

    Default projects:
    packit/ogr
    packit/requre
    packit/specfile
    packit/packit
    packit/research
    packit/weekly-roles
    packit/tokman
    packit/wait-for-copr
    packit/sandcastle
    packit/packit-service-zuul
    packit/packit-service-fedmsg
    packit/packit-service
    packit/dist-git-to-source-git
    packit/deployment
    packit/hardly
    packit/dashboard
    packit/packit.dev
    packit/private
    packit/packit-service-centosmsg
    """
    project = project or DEFAULT_PROJECTS

    click.echo("Projects:\n" + "\n".join(f"* {p}" for p in project))
    if label:
        click.echo(
            "Labels:\n" + "\n".join(f"* {label}: {weight}" for label, weight in label)
        )

    get_closed_issues_per_week(
        projects=project,
        service=GithubService(token=token),
        labels=label,
        value_without_label=value_without_label,
    )


if __name__ == "__main__":
    velocity(auto_envvar_prefix="TEAM_VELOCITY")
