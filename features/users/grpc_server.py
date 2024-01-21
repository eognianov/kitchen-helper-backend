"""gRPC server for users feature"""
from concurrent import futures
import grpc
import communication.users_pb2
import communication.users_pb2_grpc
import configuration


class UserServicer(communication.users_pb2_grpc.UsersServicer):
    def get_username(self, request, context):
        message = communication.users_pb2.UsernameResponse(username='eognianov')
        return message


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    communication.users_pb2_grpc.add_UsersServicer_to_server(UserServicer(), server=server)
    server.add_insecure_port(configuration.Config().users_grpc_server_host)
    server.start()
    server.wait_for_termination()
