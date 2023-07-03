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

You can also specify these variables in your environment:
```
export GH_USERNAME=AlexanderGrooff
export GH_ORGANIZATION=ByteInternet

export START_MONTH=$(printf "%02d" ${START_MONTH:-$(date +%m)})
export END_MONTH=$(printf "%02d" ${END_MONTH:-$(( $START_MONTH + 1 ))})

# Or you can use specific dates
export START_DATE=2023-05-01
export END_DATE=2023-05-31
```
