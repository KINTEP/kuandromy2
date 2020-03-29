from quandromy import db
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
import graphene
from quandromy.database import User, Post, Comment, Follow
from quandromy.users.utils import save_picture2

# ------------------ Graphql Schemas ------------------

# Objects Schema
class PostObject(SQLAlchemyObjectType):
    class Meta:
        model = Post
        interfaces = (graphene.relay.Node,)


class UserObject(SQLAlchemyObjectType):
    class Meta:
        model = User
        interfaces = (graphene.relay.Node,)

class CommentObject(SQLAlchemyObjectType):
    class Meta:
        model = Comment
        interfaces = (graphene.relay.Node,)

class FollowObject(SQLAlchemyObjectType):
    class Meta:
        model = Follow
        interfaces = (graphene.relay.Node,)

class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    all_posts = SQLAlchemyConnectionField(PostObject)
    all_users = SQLAlchemyConnectionField(UserObject)
    all_comments = SQLAlchemyConnectionField(CommentObject)
    all_followers = SQLAlchemyConnectionField(FollowObject)


# noinspection PyTypeChecker
schema_query = graphene.Schema(query=Query)

# Mutation Objects Schema
class CreatePost(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        describe = graphene.String(required = True)
        picture = graphene.String(required = True)
        email = graphene.String(required=True)

    post = graphene.Field(lambda: PostObject)

    def mutate(self, info, title, email, describe, picture):
        user = User.query.filter_by(email=email).first()
        post = Post()
        if user is not None:
            post.author = user
            pic = save_picture2(picture)
        post.title = title
        post.describe = describe
        post.picture = pic
        #post = Post(title=title, describe = describe, picture = pic)
        db.session.add(post)
        db.session.commit()
        return CreatePost(post=post)


class Mutation(graphene.ObjectType):
    save_post = CreatePost.Field()


# noinspection PyTypeChecker
schema_mutation = graphene.Schema(query=Query, mutation=Mutation)


