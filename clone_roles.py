import logging
import os
import random
from typing import List

from ogr.abstract import IssueStatus, Issue
from ogr.services.github.project import GithubProject
from ogr.services.github.service import GithubService

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

logging.basicConfig(level=logging.INFO)
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
            # sort the issues by created attribute from the newest
            issues.sort(key=lambda issue: issue.created, reverse=True)
            self._previous_week_issues = [
                self.get_issue_by_title(issue_title, issues)
                for issue_title in ISSUE_TITLES
            ]
        return self._previous_week_issues

    @staticmethod
    def get_issue_by_title(title: str, issues: List[Issue]):
        # issues are sorted from the most recently created
        # so the first found is the most recent
        return next(issue for issue in issues if issue.title == title)

    def _rotate_roles(self) -> List[str]:
        maintainers = [issue.assignees[0].login for issue in self.previous_week_issues]
        candidates = list(PEOPLE - set(maintainers))

        # remove responsible for the first role
        maintainers.pop(0)
        # randomly pick someone who didn't do anything last week ;)
        maintainers.append(random.choice(candidates))

        return maintainers

    def create_issues(self):
        maintainers = self._rotate_roles()

        logger.info("Creating issues:")
        for issue, new_maintainer in zip(self.previous_week_issues, maintainers):
            self.weekly_roles_project.create_issue(
                title=issue.title,
                body=issue.description,
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
