# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import communication.users_pb2 as users__pb2


class UsersStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.get_username = channel.unary_unary(
            '/users.Users/get_username',
            request_serializer=users__pb2.UsernameRequest.SerializeToString,
            response_deserializer=users__pb2.UsernameResponse.FromString,
        )


class UsersServicer(object):
    """Missing associated documentation comment in .proto file."""

    def get_username(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_UsersServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'get_username': grpc.unary_unary_rpc_method_handler(
            servicer.get_username,
            request_deserializer=users__pb2.UsernameRequest.FromString,
            response_serializer=users__pb2.UsernameResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler('users.Users', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class Users(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def get_username(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/users.Users/get_username',
            users__pb2.UsernameRequest.SerializeToString,
            users__pb2.UsernameResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
