#!/usr/bin/env python
import json
import os
from datetime import datetime, timedelta
from argparse import ArgumentParser
from typing import Iterator, List, Optional
from github import Github, GithubException
from github.Organization import Organization
from github.PullRequest import PullRequest
from github.Commit import Commit


TEXT_LIMIT = int(os.environ.get("TEXT_LIMIT", 140))
if os.environ.get("START_MONTH"):
    year = datetime.now().year
    DEFAULT_START_DATE = datetime(
        year=year, month=int(os.environ["START_MONTH"]), day=1
    )
    DEFAULT_END_DATE = datetime(year=year, month=int(os.environ["END_MONTH"]), day=1)
    if DEFAULT_END_DATE < DEFAULT_START_DATE:
        DEFAULT_START_DATE = DEFAULT_START_DATE.replace(year=year - 1)
else:
    DEFAULT_START_DATE = os.environ.get(
        "START_DATE", datetime.today() - timedelta(days=7)
    )
    DEFAULT_END_DATE = os.environ.get("END_DATE", datetime.today())


def valid_date_arg(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")


def get_args():
    parser = ArgumentParser(
        description="Retrieve all commits from the given Github organization"
    )
    parser.add_argument(
        "-o",
        "--organization",
        help="Name of the Github organization",
        default=os.environ.get("GH_ORGANIZATION"),
    )
    parser.add_argument(
        "-u",
        "--username",
        help="Username to filter on",
        default=os.environ.get("GH_USERNAME"),
    )
    parser.add_argument(
        "-s",
        "--startdate",
        type=valid_date_arg,
        help="Date from which to look for",
        default=DEFAULT_START_DATE,
    )
    parser.add_argument(
        "-e",
        "--enddate",
        type=valid_date_arg,
        help="Date until which to look for",
        default=DEFAULT_END_DATE,
    )

    parser.add_argument(
        "-l",
        "--label-pattern",
        help="Label pattern to filter on",
        default=os.environ.get("GH_LABEL_PATTERN"),
    )
    parser.add_argument(
        "-t",
        "--type",
        help="Type of search",
        default="commits",
        choices=["commits", "prs"],
    )
    return parser.parse_args()


def init_github(org_name):
    print("Getting Github organization {}".format(org_name))
    g = Github(os.environ["GITHUB_ACCESS_TOKEN"])
    return g.get_organization(org_name)


def get_commits_for_org(
    org: Organization, startdate: datetime, enddate, username
) -> List[Commit]:
    commit_kwargs = {"since": startdate, "until": enddate}
    if username:
        commit_kwargs.update({"author": username})
    org_commits = []

    print(f"Looking for repos in organization {org}")
    repos = list(org.get_repos())

    print(
        f"Checking for commits from {username} in {len(repos)} repos, ordered by last updated repos"
    )
    print("You can interrupt at any moment to print results found so far")
    print()
    try:
        # Start with newest repos first
        for repo in reversed(repos):
            try:
                repo_commits = list(repo.get_commits(**commit_kwargs))
            except GithubException as e:
                print("Got error for repo {}: {}".format(repo.name, e))
                continue
            print("Found {} commits in repo {}".format(len(repo_commits), repo.name))
            org_commits.extend(repo_commits)
    except KeyboardInterrupt:
        print("Interrupted. Returning results found so far")

    print()
    return org_commits


def clip_long_text(s):
    return s[:TEXT_LIMIT] + ".." if len(s) > TEXT_LIMIT else s


def pprint_commits(commits: List[Commit]):
    sorted_commits = sorted(commits, key=lambda c: c.commit.author.date)
    labels_per_day = {}
    for c in sorted_commits:
        commit_date = c.commit.author.date.strftime("%Y-%m-%d(%a)")
        msg_kwargs = {
            "date": commit_date,
            "author": c.commit.author.name,
            "msg": clip_long_text(c.commit.message.strip().replace("\n", " ")),
        }
        labels_per_day.setdefault(commit_date, {})
        if pr := get_pr_for_commit(c):
            print(
                "{date} {author:>20} [{labels}]: {msg}".format(
                    labels=",".join(sorted([l.name for l in pr.labels])), **msg_kwargs
                )
            )
            for label in pr.labels:
                labels_per_day[commit_date][label.name] = (
                    labels_per_day[commit_date][label.name] + 1
                    if label.name in labels_per_day[commit_date]
                    else 1
                )
        else:
            print("{date} {author:>20}: {msg}".format(**msg_kwargs))
    print(f"Labels per day: {json.dumps(labels_per_day, indent=2)}")


def pprint_prs(prs, label_pattern=None):
    sorted_prs = sorted(prs, key=lambda pr: pr.created_at)
    for pr in sorted_prs:
        matching_labels = [
            l.name for l in pr.labels if label_pattern and label_pattern in l.name
        ]
        print(
            "{date} {author:>20} ({labels}): {msg}".format(
                date=pr.created_at.strftime("%Y-%m-%d(%a)"),
                author=pr.user.login,
                msg=clip_long_text(pr.title.strip().replace("\n", " ")),
                labels=",".join(matching_labels),
            )
        )


def get_pr_for_commit(commit: Commit) -> Optional[PullRequest]:
    try:
        prs = commit.get_pulls()
        return list(prs)[0]
    except:
        return


def main():
    args = get_args()
    org = init_github(args.organization)
    commits = get_commits_for_org(org, args.startdate, args.enddate, args.username)
    pprint_commits(commits)


if __name__ == "__main__":
    main()
