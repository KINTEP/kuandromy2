from flask import Flask, redirect, url_for
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from flask_login import login_user, current_user
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin, SQLAlchemyStorage
from flask_dance.consumer import oauth_authorized
from sqlalchemy.orm.exc import NoResultFound
from quandromy.database import OAuth
from quandromy import db

facebook_blueprint = make_facebook_blueprint()

facebook_blueprint.storage = SQLAlchemyStorage(OAuth, db.session, user=current_user)

@oauth_authorized.connect_via(facebook_blueprint)
def facebook_logged_in(blueprint, token):

    account_info = blueprint.session.get('/me')

    if account_info.ok:
        account_info_json = account_info.json()
        username = account_info_json['name']

        query = User.query.filter_by(username=username)

        try:
            user = query.one()
        except NoResultFound:
            user = User(username=username)
            db.session.add(user)
            db.session.commit()

        login_user(user)


@facebook_blueprint.route("/facebook")
def facebook():
    if not facebook.authorized:
        return redirect(url_for("facebook.login"))
    resp = facebook.get("/me")
    assert resp.ok, resp.text
    return "You are {name} on Facebook".format(name=resp.json()["name"])

