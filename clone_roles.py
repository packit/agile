import os
import random
import logging
from typing import List

from ogr.services.github.issue import GithubIssue
from ogr.services.github.project import GithubProject
from ogr.services.github.service import GithubService

from ogr.abstract import IssueStatus

PEOPLE = {
    "lachmanfrantisek",
    "FrNecas",
    "csomh",
    "jpopelka",
    "lbarcziova",
    "mfocko",
    "majamassarini",
    "nforro",
    "TomasTomecek",
}

ISSUE_TITLES = [
    "Service Guru",
    "Chief of Monitors",
    "Kanban Lead",
    "Release Responsible",
    "CI Hacker",
    "Community Shepherd",
]

logger = logging.getLogger(__name__)


class RotationHelper:
    def __init__(self, token):
        self.weekly_roles_project: GithubProject = GithubService(
            token=token
        ).get_project(repo="weekly-roles", namespace="packit")
        self._previous_week_issues = None

    @property
    def previous_week_issues(self):
        if not self._previous_week_issues:
            issues = self.weekly_roles_project.get_issue_list(
                labels=["roles"], status=IssueStatus.all
            )
            self._previous_week_issues = [
                self.get_issue_by_title(issue_title, issues)
                for issue_title in ISSUE_TITLES
            ]
        return self._previous_week_issues

    @staticmethod
    def get_issue_by_title(title: str, issues: List[GithubIssue]):
        return [issue for issue in issues if issue.title == title][0]

    def _rotate_roles(self) -> List[str]:
        maintainers = [issue.assignees[0].login for issue in self.previous_week_issues]
        candidates = list(PEOPLE - set(maintainers))

        # remove responsible of the first role
        maintainers.pop(0)
        # randomly pick on someone that didn't do anything last week ;)
        maintainers.append(random.choice(candidates))

        return maintainers

    def create_issues(self):
        maintainers = self._rotate_roles()

        logger.info("Creating issues:")
        for issue, new_maintainer in zip(self.previous_week_issues, maintainers):
            self.weekly_roles_project.create_issue(
                title=issue.title,
                description=issue.description,
                assignees=[new_maintainer],
                labels=["roles"],
            )
            logger.info(f"Role: {issue.title}, assignee: {new_maintainer}")

    def close_previous_week_issues(self):
        logger.info("Closing opened issues from previous week.")
        for issue in self.previous_week_issues:
            if issue.status == IssueStatus.open:
                issue.close()


if __name__ == "__main__":
    helper = RotationHelper(os.getenv("TOKEN"))
    helper.create_issues()
    helper.close_previous_week_issues()
