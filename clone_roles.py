import logging
import os
import random
from typing import List, Optional, Mapping

from ogr.abstract import IssueStatus, Issue
from ogr.services.github.project import GithubProject
from ogr.services.github.service import GithubService

ROLE_LABEL = "kind/role"
ISSUE_TITLES = [
    "Service Guru",
    "Release Responsible",
    "Chief of Monitors",
    "Kanban Lead",
    "Community Shepherd",
    "Skald",
]
MAINTAINERS_ALLOWED_JOBS = {
    "majamassarini": ISSUE_TITLES,  # Can do any job
    "lbarcziova": ISSUE_TITLES,
    "m-blaha": ISSUE_TITLES,
    "nforro": ISSUE_TITLES,
    "TomasTomecek": ISSUE_TITLES,
    "betulependule": ISSUE_TITLES,  # akucerov
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RotationHelper:
    def __init__(self, token):
        self.weekly_roles_project: GithubProject = GithubService(
            token=token
        ).get_project(repo="agile", namespace="packit")
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

    def get_last_done_job(self) -> Mapping[str, Optional[str]]:
        maintainers_last_job = {k: None for k in MAINTAINERS_ALLOWED_JOBS.keys()}
        for issue in self.previous_week_issues:
            job_title = issue.title
            assignee = issue.assignees[0].login if issue.assignees else None
            if assignee in maintainers_last_job:
                maintainers_last_job[assignee] = job_title
        return maintainers_last_job

    def choose_maintainer(
        self,
        job_title: str,
        maintainers_last_job: Mapping[str, Optional[str]],
        already_assigned: List[str],
    ) -> str:
        eligible_maintainers = []
        for maintainer, jobs in MAINTAINERS_ALLOWED_JOBS.items():
            if job_title in jobs and maintainer not in already_assigned:
                eligible_maintainers.append(maintainer)

        # If no eligible maintainers are available (all already assigned),
        # we need to pick someone who can do this job even if they're already assigned
        if not eligible_maintainers:
            for maintainer, jobs in MAINTAINERS_ALLOWED_JOBS.items():
                if job_title in jobs:
                    eligible_maintainers.append(maintainer)

        # If maintainers have done nothing previous week, choose between them
        best_fits = []
        for maintainer in eligible_maintainers:
            if maintainers_last_job[maintainer] is None:
                best_fits.append(maintainer)

        if best_fits:
            return random.choice(best_fits)

        # If maintainers' next role is this, choose between them
        best_fits = []
        for maintainer in eligible_maintainers:
            jobs = MAINTAINERS_ALLOWED_JOBS[maintainer]
            last_job = maintainers_last_job[maintainer]
            if last_job and last_job in jobs:
                new_job_index = (jobs.index(last_job) + 1) % len(jobs)
                if jobs[new_job_index] == job_title:
                    best_fits.append(maintainer)

        if best_fits:
            return random.choice(best_fits)

        # Otherwise choose between all eligible
        return random.choice(eligible_maintainers)

    def rotate_roles(self) -> List[str]:
        """
        Finds eligible maintainers who can do the job.
        Prioritizes maintainers who didn't have a job last time.
        If all eligible maintainers had jobs, it finds the next job in rotation for each maintainer.
        If no clear next-in-rotation, it picks randomly
        """
        maintainers_last_job = self.get_last_done_job()
        maintainers = []
        already_assigned: List[str] = []

        for job_title in ISSUE_TITLES:
            maintainer = self.choose_maintainer(
                job_title, maintainers_last_job, already_assigned
            )
            maintainers.append(maintainer)
            already_assigned.append(maintainer)

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
