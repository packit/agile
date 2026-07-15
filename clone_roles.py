from __future__ import annotations

import logging
import os
import random

from ogr.abstract import IssueStatus, Issue
from ogr.services.github.project import GithubProject
from ogr.services.github.service import GithubService

ROLE_LABEL = "kind/role"
WEEKLY_ROLES = [
    "Service Guru",
    "Release Responsible",
    "Chief of Monitors",
    "Kanban Lead",
    "Community Shepherd",
]
INDEPENDENT_ROLE_ROTATIONS = {
    "Skald": ["lbarcziova", "majamassarini", "opohorel", "TomasTomecek", "nforro"],
}
INDEPENDENT_ROLES = list(INDEPENDENT_ROLE_ROTATIONS)
ISSUE_TITLES = WEEKLY_ROLES + INDEPENDENT_ROLES
WEEKLY_MAINTAINERS = [
    "majamassarini",
    "lbarcziova",
    "mfocko",
    "nforro",
    "betulependule",
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RotationHelper:
    def __init__(self, token):
        self.weekly_roles_project: GithubProject = GithubService(
            token=token
        ).get_project(repo="agile", namespace="packit")
        self._all_role_issues = None
        self._previous_week_issues = None

    @property
    def all_role_issues(self):
        if self._all_role_issues is None:
            self._all_role_issues = self.weekly_roles_project.get_issue_list(
                labels=[ROLE_LABEL], status=IssueStatus.all
            )
            self._all_role_issues.sort(key=lambda issue: issue.created, reverse=True)
        return self._all_role_issues

    @property
    def previous_week_issues(self):
        if not self._previous_week_issues:
            self._previous_week_issues = [
                self.get_issue_by_title(issue_title, self.all_role_issues)
                for issue_title in ISSUE_TITLES
            ]
        return self._previous_week_issues

    @staticmethod
    def get_issue_by_title(title: str, issues: list[Issue]):
        # issues are sorted from the most recently created
        # so the first found is the most recent
        return next(issue for issue in issues if issue.title == title)

    def get_last_done_job(self) -> dict[str, str | None]:
        last_job: dict[str, str | None] = {m: None for m in WEEKLY_MAINTAINERS}
        for issue in self.previous_week_issues:
            if issue.title in INDEPENDENT_ROLES:
                continue
            assignee = issue.assignees[0].login if issue.assignees else None
            if assignee in last_job:
                last_job[assignee] = issue.title
        return last_job

    def choose_maintainer(
        self,
        job_title: str,
        maintainers_last_job: dict[str, str | None],
        already_assigned: list[str],
    ) -> str:
        eligible = [m for m in WEEKLY_MAINTAINERS if m not in already_assigned]
        if not eligible:
            eligible = list(WEEKLY_MAINTAINERS)

        best_fits = [m for m in eligible if maintainers_last_job[m] is None]
        if best_fits:
            return random.choice(best_fits)

        best_fits = []
        for m in eligible:
            last = maintainers_last_job[m]
            if last and last in WEEKLY_ROLES:
                next_idx = (WEEKLY_ROLES.index(last) + 1) % len(WEEKLY_ROLES)
                if WEEKLY_ROLES[next_idx] == job_title:
                    best_fits.append(m)

        if best_fits:
            return random.choice(best_fits)

        return random.choice(eligible)

    def choose_independent_role(self, job_title: str) -> str:
        rotation = INDEPENDENT_ROLE_ROTATIONS[job_title]
        for issue in self.all_role_issues:
            if issue.title == job_title and issue.assignees:
                last_assignee = issue.assignees[0].login
                if last_assignee in rotation:
                    idx = rotation.index(last_assignee)
                    return rotation[(idx + 1) % len(rotation)]
        return rotation[0]

    def rotate_roles(self) -> list[str]:
        """
        Finds eligible maintainers who can do the job.
        Prioritizes maintainers who didn't have a job last time.
        If all eligible maintainers had jobs, it finds the next job in rotation for each maintainer.
        If no clear next-in-rotation, it picks randomly.
        Independent roles (e.g. Skald) follow a fixed rotation order,
        advancing to the next person based on the current assignee.
        """
        maintainers_last_job = self.get_last_done_job()
        maintainers = []
        already_assigned: list[str] = []

        for job_title in ISSUE_TITLES:
            if job_title in INDEPENDENT_ROLES:
                maintainer = self.choose_independent_role(job_title)
            else:
                maintainer = self.choose_maintainer(
                    job_title, maintainers_last_job, already_assigned
                )
                already_assigned.append(maintainer)
            maintainers.append(maintainer)

        return maintainers

    def create_issues(self):
        maintainers = self.rotate_roles()
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
