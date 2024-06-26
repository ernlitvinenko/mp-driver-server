from strawberry.fastapi import GraphQLRouter

from core.transport.graphql.schema import schema

router = GraphQLRouter(schema=schema)
