#!/usr/bin/env python
import os
from datetime import datetime, timedelta
from argparse import ArgumentParser
from github import Github, GithubException


TEXT_LIMIT = 140


def valid_date_arg(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")


def get_args():
    parser = ArgumentParser(description="Retrieve all commits from the given Github organization")
    parser.add_argument("organization", help="Name of the Github organization")
    parser.add_argument("-u", "--username", help="Username to filter on")
    parser.add_argument("-s", "--startdate", type=valid_date_arg,
                        help="Date from which to look for", default=datetime.today() - timedelta(days=7))
    parser.add_argument("-e", "--enddate", type=valid_date_arg,
                        help="Date until which to look for", default=datetime.today())
    return parser.parse_args()


def init_github(org_name):
    print("Getting Github organization {}".format(org_name))
    g = Github(os.environ['GITHUB_ACCESS_TOKEN'])
    return g.get_organization(org_name)


def get_commits_for_org(org, startdate, enddate, username):
    commit_kwargs = {'since': startdate, 'until': enddate}
    if username:
        commit_kwargs.update({'author': username})
    org_commits = []
    for repo in org.get_repos():
        try:
            repo_commits = list(repo.get_commits(**commit_kwargs))
        except GithubException as e:
            print("Got error for repo {}: {}".format(repo.name, e))
            continue
        print("Found {} commits in repo {}".format(len(repo_commits), repo.name))
        org_commits.extend(repo_commits)
    return org_commits


def clip_long_text(s):
    return s[:TEXT_LIMIT] + ".." if len(s) > TEXT_LIMIT else s


def pprint_commits(commits):
    sorted_commits = sorted(commits, key=lambda c: c.commit.author.date)
    for c in sorted_commits:
        print("{date} {author:>20}: {msg}".format(
            date=c.commit.author.date.strftime("%Y-%m-%d(%a)"),
            author=c.commit.author.name,
            msg=clip_long_text(c.commit.message.strip().replace("\n", " "))
        ))


def main():
    args = get_args()
    org = init_github(args.organization)
    commits = get_commits_for_org(org, args.startdate, args.enddate, args.username)
    pprint_commits(commits)



if __name__ == "__main__":
    main()

