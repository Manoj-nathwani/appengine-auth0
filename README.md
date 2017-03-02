# Auth0 + Google App Engine starter template

This is a simple Google appengine app which combines [Auth0](https://auth0.com) for auth and uses [Memcache](https://cloud.google.com/appengine/docs/standard/python/memcache/) for stateless sessions on webapp2. To keep the project as flask-like as possible; i'm using jinja2 for templating and the requests library which is being [monkey patched to appengine's urlfetch library](https://cloud.google.com/appengine/docs/standard/python/issue-requests).

# Appengine commands

### Testing locally
```
$ dev_appserver.py app.yaml
```

### Deploying
```
$ gcloud app deploy app.yaml
```

### Adding libraries
```
$ rm -rf lib/*
$ pip install -t lib -r requirements.txt
```
