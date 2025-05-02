import logging
import os
import random
from typing import List

from ogr.abstract import IssueStatus, Issue
from ogr.services.github.project import GithubProject
from ogr.services.github.service import GithubService

ROLE_LABEL = "kind/role"
PEOPLE = {
    "lachmanfrantisek",
    "lbarcziova",
    "mfocko",
    "majamassarini",
    "nforro",
}

RESTRICTED_PEOPLE = {
    "lachmanfrantisek",
    "majamassarini",
}

ONE_TIME_ACTION_ROLES = ["Service Guru", "Release Responsible"]
GENERAL_ROLES = ["Chief of Monitors", "Kanban Lead", "Community Shepherd"]

ISSUE_TITLES = ONE_TIME_ACTION_ROLES + GENERAL_ROLES

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
                labels=[ROLE_LABEL], status=IssueStatus.all
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
        candidates = list((PEOPLE - RESTRICTED_PEOPLE) - set(maintainers))
        random.shuffle(candidates)

        # rotate between Maja and Franta for one time action roles temporarily
        maintainers[:2] = (
            ["majamassarini", "lachmanfrantisek"]
            if maintainers[0] == "lachmanfrantisek"
            else ["lachmanfrantisek", "majamassarini"]
        )

        for i in range(2, len(maintainers)):
            if maintainers[i] not in PEOPLE:
                maintainers[i] = (
                    candidates.pop()
                    if candidates
                    else random.choice(list(PEOPLE - RESTRICTED_PEOPLE))
                )

        maintainers[2:] = maintainers[3:] + [maintainers[2]]

        return maintainers

    def create_issues(self):
        maintainers = self._rotate_roles()

        logger.info("Creating issues:")
        for issue, new_maintainer in zip(self.previous_week_issues, maintainers):
            # make all tasks not done
            new_description = issue.description.replace(" [x]", " [ ]")
            self.weekly_roles_project.create_issue(
                title=issue.title,
                body=new_description,
                assignees=[new_maintainer],
                labels=[ROLE_LABEL],
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
