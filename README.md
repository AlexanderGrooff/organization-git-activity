## Development

Create a new Personal access token under https://github.com/settings/tokens, give it proper permissions according to your use case.

```
git clone git@github.com:AlexanderGrooff/organization-git-activity.git
cd organization-git-activity
mkvirtualenv organization-git-activity -a .
pip install -r requirements.txt
```

Once you've got it set up, you can find commits by running a command like the following:
```
GITHUB_ACCESS_TOKEN="some-api-token" ./main.py ByteInternet -u "AlexanderGrooff"
```
