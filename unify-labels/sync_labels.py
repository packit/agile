#!/usr/bin/env python3

import itertools
import os
from collections.abc import Iterator
from dataclasses import dataclass, field

import click
from github import Auth, Github, Repository
from github import Label as GithubLabel


@dataclass
class Label:
    name: str
    color: str | None = None
    description: str | None = None
    sublabels: list["Label"] = field(default_factory=list)

    def __iter__(self) -> Iterator["Label"]:
        if not self.sublabels:
            yield self
            return

        yield from (
            Label(
                name=f"{self.name}/{sublabel.name}",
                color=sublabel.color or self.color,
                description=sublabel.description or self.description,
            )
            for category in self.sublabels
            for sublabel in category
        )


LABELS: list[Label] = [
    # Area
    Label(
        name="area",
        color="e4f3f4",
        sublabels=[
            # Packit-based area
            Label(name="general", description="Not tied to a specific area"),
            Label(name="cli", description="Impact on packit's command-line interface"),
            Label(name="config", description="Related to the configuration"),
            Label(name="database", description="Related to the database"),
            Label(name="testing", description="Related to internal tests"),
            Label(name="user-experience", description="Related to the UX"),
            Label(name="other", description="Not specific to any other of the areas"),
            Label(name="source-git", description="Upstream + downstream in one repo"),
            Label(name="api", description="API of Packit"),
            Label(name="dashboard", description="Related to the Packit Dashboard"),
            Label(name="deployment", description="Related to the Packit's deployment"),
            # Git forges
            Label(name="github", description="GitHub-forge related", color="FBCA04"),
            Label(name="gitlab", description="GitLab-forge related", color="FBCA04"),
            Label(name="forgejo", description="Forgejo-forge related", color="FBCA04"),
            # Integrated services
            Label(
                name="copr",
                description="Related to the Copr integration",
                color="3c6eb4",
            ),
            Label(
                name="image-builder",
                description="Related to the integration with Image Builder",
                color="3c6eb4",
            ),
            Label(
                name="testing-farm",
                description="Related to the integration with Testing Farm",
                color="3c6eb4",
            ),
            Label(
                name="openscanhub",
                description="Related to the OpenScanHub integration",
                color="3c6eb4",
            ),
            # Distro ecosystems
            Label(
                name="fedora", description="Related to Fedora ecosystem", color="51a2da"
            ),
            Label(
                name="fedora-ci",
                description="Related to the Fedora CI service",
                color="51a2da",
            ),
            Label(
                name="rhel-ecosystem",
                description="Related to RHEL, CentOS Stream, etc.",
                color="EE0000",
            ),
        ],
    ),
    # Gain
    Label(
        name="gain",
        sublabels=[
            Label(
                name="low",
                color="f2ca92",
                description="Doesn't bring much value to users",
            ),
            Label(
                name="high",
                color="e59728",
                description="Brings a lot of value to users",
            ),
        ],
    ),
    # Impact
    Label(
        name="impact",
        sublabels=[
            Label(
                name="low", color="cfbddd", description="Affects only few of the users"
            ),
            Label(name="high", color="a07cbc", description="Affects a lot of users"),
        ],
    ),
    # Kind
    Label(
        name="kind",
        color="1D76DB",
        sublabels=[
            Label(
                name="bug",
                color="D93F0B",
                description="An unexpected problem or behavior",
            ),
            Label(name="documentation", description="Improvements to docs"),
            Label(name="feature", description="A request, idea, or new functionality"),
            Label(
                name="internal", description="Task that doesn't affect users directly"
            ),
            Label(name="other", description="A specific piece of work"),
            Label(
                name="technical-debt", description="Consequences of previous decisions"
            ),
            Label(name="role", description="Regular chore for the role rotation"),
            Label(name="security", color="e00f16", description="Security concern"),
            Label(
                name="recurring",
                description="Recurring task that needs to be done periodically",
            ),
        ],
    ),
    # Complexity
    Label(
        name="complexity",
        color="bbed97",
        sublabels=[
            Label(
                name="single-task",
                description="Regular task; should be done within days",
            ),
            Label(
                name="epic",
                description="Lots of work ahead; planning/design is required",
            ),
        ],
    ),
    # PR states
    Label(
        name="do-not-merge",
        color="D93F0B",
        description="Do not merge! Work in progress",
    ),
    Label(name="mergeit", color="0E8A16", description="Merge via Zuul"),
    Label(name="needs-review", color="F81880", description="Requires review"),
    Label(name="ready-for-review", color="18e033", description="Ready for review"),
    # Events
    Label(
        name="events",
        color="6318F9",
        sublabels=[
            Label(name="GSOC", description="Contribution from the GSOC mentoring"),
            Label(name="Hacktoberfest", description="Participation in Hacktoberfest"),
            Label(
                name="Outreachy",
                description="Contribution from the Outreachy mentoring",
            ),
        ],
    ),
    # Miscellaneous labels
    Label(
        name="blocked", color="D93F0B", description="Blocked on external dependencies"
    ),
    Label(name="demo", color="5319E7", description="Should be accompanied by a demo"),
    Label(name="discuss", color="316dc1", description="To be discussed within team"),
    Label(name="good-first-issue", color="7057ff", description="Good for newcomers"),
    Label(
        name="release",
        color="ededed",
        description="Denotes a PR/issue involved in a release",
    ),
    Label(
        name="resource-reduction",
        color="81AA58",
        description="Can reduce required resources",
    ),
    Label(
        name="workaround-exists",
        color="000000",
        description="There is a workaround that can be used in the meantime",
    ),
]
EXPANDED_LABELS = {label.name: label for label in itertools.chain.from_iterable(LABELS)}

RENAME = [
    ("GSOC", "events/GSOC"),
    ("Hacktoberfest", "events/Hacktoberfest"),
    ("Outreachy", "events/Outreachy"),
    ("security", "kind/security"),
    ("source-git", "area/source-git"),
    ("API", "area/api"),
    ("dashboard", "area/dashboard"),
    ("deployment", "area/deployment"),
    ("recurring", "kind/recurring"),
]


def get_labels(repo: Repository) -> dict[str, GithubLabel]:
    return {label.name: label for label in repo.get_labels()}


def handle_repo(repo: Repository):
    if repo.archived:
        click.secho(f"  [INFO] Skipping archived {repo.full_name}", fg="yellow")
        return

    click.secho(f"  [INFO] Syncing {repo.full_name}")

    current_labels = get_labels(repo)

    for label in EXPANDED_LABELS.values():
        if existing_label := current_labels.get(label.name):
            if (
                existing_label.color == label.color
                and existing_label.description == label.description
            ):
                continue
            click.secho(f"    [INFO] Updating label {label.name}", fg="yellow")
            existing_label.edit(
                name=label.name, color=label.color, description=label.description
            )
        else:
            click.secho(f"    [INFO] Creating label {label.name}", fg="green")
            repo.create_label(
                name=label.name,
                description=label.description,
                color=label.color,
            )

    current_labels = get_labels(repo)
    for old_name, new_name in RENAME:
        old_label = current_labels.get(old_name)
        if old_label is None:
            # if there's no label with the old name, skip
            continue

        click.secho(f"    [INFO] Renaming {old_name} to {new_name}", fg="yellow")

        # check if there is a need to get rid of the new name
        if new_name in current_labels:
            click.secho(f"    [INFO] Deleting the new label {new_name}", fg="red")
            current_labels[new_name].delete()

        # update the old one
        label = EXPANDED_LABELS[new_name]
        old_label.edit(name=new_name, color=label.color, description=label.description)


def main():
    click.secho("[INFO] Authenticating against GitHub", fg="blue")
    auth = Auth.Token(os.getenv("GITHUB_TOKEN"))
    g = Github(auth=auth)

    click.secho("[INFO] Fetching Packit org", fg="blue")
    org = g.get_organization("packit")

    click.secho("[INFO] Syncing repos", fg="blue")
    for repo in org.get_repos():
        handle_repo(repo)


if __name__ == "__main__":
    main()
