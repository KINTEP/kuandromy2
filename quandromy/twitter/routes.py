from flask import Flask, redirect, url_for
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
from flask import Flask, redirect, url_for
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
from flask_login import login_user, current_user
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin, SQLAlchemyStorage
from flask_dance.consumer import oauth_authorized
from sqlalchemy.orm.exc import NoResultFound
from quandromy.database import OAuth
from quandromy import db

twitter_blueprint = make_twitter_blueprint()

twitter_blueprint.storage = SQLAlchemyStorage(OAuth, db.session, user=current_user)

@oauth_authorized.connect_via(twitter_blueprint)
def twitter_logged_in(blueprint, token):

    account_info = blueprint.session.get('/user')

    if account_info.ok:
        account_info_json = account_info.json()
        username = account_info_json['screen_name']
        country = account_info_json["trend_location"][0]["country"]

        query = User.query.filter_by(username=username)

        try:
            user = query.one()
        except NoResultFound:
            user = User(username=username, counrty = country)
            db.session.add(user)
            db.session.commit()

        login_user(user)

@twitter_blueprint.route("/twitter")
def twitter():
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))
    resp = twitter.get("/user")
    print(resp.json())
    assert resp.ok
    return "You are @{login} on Twitter".format(login=resp.json()["screen_name"])


