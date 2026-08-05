#!/usr/bin/env python3
"""Sync Jira ticket URLs onto linked GitHub issues.

For every PACKIT Jira ticket with the ``upstream`` label, fetches its web
links (remote links), finds any that point to GitHub issues, and sets the
``Jira ticket`` issue field on those GitHub issues to the Jira ticket URL.

Authentication:
  JIRA_EMAIL  – Atlassian account email (required)
  JIRA_TOKEN  – Atlassian API token (required)
  GITHUB_TOKEN – GitHub token with repo + org access (required, or use `gh auth`)

Usage:
  export JIRA_EMAIL=you@redhat.com
  export JIRA_TOKEN=...
  ./sync_jira_to_github.py
  ./sync_jira_to_github.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from typing import Any, Iterator

import requests
from tqdm import tqdm

DEFAULT_JIRA_URL = "https://redhat.atlassian.net"
DEFAULT_JQL = (
    'project = PACKIT AND labels = "upstream" AND labels != "closed-upstream"'
    " AND statusCategory != Done ORDER BY key ASC"
)
PAGE_SIZE = 100
FIELDS = ["summary"]

JIRA_TICKET_FIELD_ID = "IFT_kgDOArAWcw"

GITHUB_ISSUE_RE = re.compile(r"https://github\.com/([^/]+)/([^/]+)/issues/(\d+)")


def jira_get(url: str, email: str, token: str) -> Any:
    try:
        response = requests.get(url, auth=(email, token))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as exc:
        raise SystemExit(
            f"Jira API error {exc.response.status_code} for {url}:\n{exc.response.text}"
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise SystemExit(f"Failed to reach Jira at {url}: {exc}") from exc


def jira_post(url: str, email: str, token: str, body: dict[str, Any]) -> dict[str, Any]:
    try:
        response = requests.post(url, json=body, auth=(email, token))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as exc:
        raise SystemExit(
            f"Jira API error {exc.response.status_code} for {url}:\n{exc.response.text}"
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise SystemExit(f"Failed to reach Jira at {url}: {exc}") from exc


def iter_issues(
    jira_url: str, email: str, token: str, jql: str
) -> Iterator[dict[str, Any]]:
    search_url = f"{jira_url.rstrip('/')}/rest/api/3/search/jql"
    next_page_token: str | None = None

    while True:
        body: dict[str, Any] = {
            "jql": jql,
            "maxResults": PAGE_SIZE,
            "fields": FIELDS,
        }
        if next_page_token:
            body["nextPageToken"] = next_page_token

        data = jira_post(search_url, email, token, body)
        yield from data.get("issues", [])

        next_page_token = data.get("nextPageToken")
        if not next_page_token or data.get("isLast", True):
            break


def fetch_web_links(jira_url: str, email: str, token: str, issue_key: str) -> list[str]:
    url = f"{jira_url.rstrip('/')}/rest/api/3/issue/{issue_key}/remotelink"
    links = jira_get(url, email, token)
    return [
        link["object"]["url"] for link in links if (link.get("object") or {}).get("url")
    ]


def ticket_url(jira_url: str, issue_key: str) -> str:
    return f"{jira_url.rstrip('/')}/browse/{issue_key}"


def gh_graphql(query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    if variables:
        for key, value in variables.items():
            cmd += ["-F", f"{key}={value}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(f"GitHub API error:\n{result.stderr}")
    data = json.loads(result.stdout)
    if "errors" in data:
        raise SystemExit(
            f"GitHub GraphQL errors:\n{json.dumps(data['errors'], indent=2)}"
        )
    return data


def fetch_github_issue_info(
    owner: str, repo: str, number: int
) -> tuple[str, str] | None:
    """Return (node_id, sort_timestamp) or None if the issue is inaccessible.

    sort_timestamp is the ISO-8601 timestamp of the latest comment, falling
    back to the issue's own createdAt when there are no comments.
    """
    query = """
    query($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $number) {
          id
          createdAt
          comments(last: 1) {
            nodes {
              createdAt
            }
          }
        }
      }
    }
    """
    cmd = [
        "gh",
        "api",
        "graphql",
        "-f",
        f"query={query}",
        "-f",
        f"owner={owner}",
        "-f",
        f"repo={repo}",
        "-F",
        f"number={number}",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    data = json.loads(result.stdout)
    issue = (data.get("data") or {}).get("repository", {}).get("issue")
    if not issue:
        return None
    node_id = issue["id"]
    created_at = issue["createdAt"]
    comment_nodes = issue.get("comments", {}).get("nodes", [])
    sort_ts = comment_nodes[-1]["createdAt"] if comment_nodes else created_at
    return node_id, sort_ts


def set_jira_field(issue_node_id: str, jira_ticket: str, dry_run: bool) -> bool:
    if dry_run:
        return True

    mutation = """
    mutation($issueId: ID!, $fieldId: ID!, $value: String!) {
      setIssueFieldValue(input: {
        issueId: $issueId
        issueFields: [{ fieldId: $fieldId, textValue: $value }]
      }) {
        clientMutationId
      }
    }
    """
    cmd = [
        "gh",
        "api",
        "graphql",
        "-f",
        f"query={mutation}",
        "-f",
        f"issueId={issue_node_id}",
        "-f",
        f"fieldId={JIRA_TICKET_FIELD_ID}",
        "-f",
        f"value={jira_ticket}",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"    ERROR: {result.stderr.strip()}", file=sys.stderr)
        return False
    data = json.loads(result.stdout)
    if "errors" in data:
        print(f"    ERROR: {json.dumps(data['errors'])}", file=sys.stderr)
        return False
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Set the 'Jira ticket' GitHub issue field from Jira upstream tickets.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be updated without making any changes.",
    )
    parser.add_argument(
        "--jql",
        default=None,
        help="Override the JQL query used to fetch Jira issues.",
    )
    parser.add_argument(
        "--url",
        default=os.environ.get("JIRA_URL", DEFAULT_JIRA_URL),
        help=f"Jira base URL (env JIRA_URL, default: {DEFAULT_JIRA_URL}).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    email = os.environ.get("JIRA_EMAIL")
    token = os.environ.get("JIRA_TOKEN")
    if not email or not token:
        print(
            "Set JIRA_EMAIL and JIRA_TOKEN environment variables.\n"
            "Create a token at: https://id.atlassian.com/manage-profile/security/api-tokens",
            file=sys.stderr,
        )
        return 1

    jql = args.jql or DEFAULT_JQL

    print(f"# JQL: {jql}", file=sys.stderr)
    if args.dry_run:
        print("# Dry run — no changes will be made.", file=sys.stderr)

    updated = 0
    skipped = 0
    errors = 0

    # Collect all (jira_key, owner, repo, number) tuples across all Jira issues.
    pending: list[tuple[str, str, str, int]] = []
    for issue in tqdm(
        iter_issues(args.url, email, token, jql), desc="Fetching web links"
    ):
        key = issue["key"]
        web_links = fetch_web_links(args.url, email, token, key)
        for link in web_links:
            m = GITHUB_ISSUE_RE.match(link)
            if m:
                pending.append((key, m.group(1), m.group(2), int(m.group(3))))

    # Fetch GitHub issue info and sort by the latest-activity timestamp ascending.
    enriched: list[tuple[str, str, str, str, str, int]] = []
    inaccessible: list[tuple[str, str, str, int]] = []
    for key, owner, repo, number in tqdm(pending, desc="Fetching GitHub issue info"):
        info = fetch_github_issue_info(owner, repo, number)
        if info is None:
            inaccessible.append((key, owner, repo, number))
        else:
            node_id, sort_ts = info
            enriched.append((sort_ts, key, node_id, owner, repo, number))

    enriched.sort(key=lambda t: t[0])

    for key, owner, repo, number in inaccessible:
        gh_url = f"https://github.com/{owner}/{repo}/issues/{number}"
        print(f"{key}")
        print(f"  SKIP  {gh_url}  (issue not found or no access)")
        skipped += 1

    for sort_ts, key, node_id, owner, repo, number in enriched:
        gh_url = f"https://github.com/{owner}/{repo}/issues/{number}"
        print(f"{key}")
        action = "DRY-RUN" if args.dry_run else "SET"
        ok = set_jira_field(node_id, key, args.dry_run)
        if ok:
            print(f"  {action}  {gh_url}  -> Jira ticket: {key}")
            updated += 1
        else:
            print(f"  ERROR  {gh_url}")
            errors += 1

    print(
        f"\nDone: {updated} updated, {skipped} skipped, {errors} errors.",
        file=sys.stderr,
    )
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
