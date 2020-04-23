
from flask import current_app
from flask_graphql import GraphQLView
from quandromy.api.schema import schema_query, schema_mutation
from flask import Blueprint

api = Blueprint("api", __name__)


# /graphql-query
api.add_url_rule('/graphql-query', view_func=GraphQLView.as_view(
    'graphql-query',
    schema=schema_query, graphiql=True
))

# /graphql-mutation
api.add_url_rule('/graphql-mutation', view_func=GraphQLView.as_view(
    'graphql-mutation',
    schema=schema_mutation, graphiql=True
))
