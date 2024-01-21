"""gRPC server for images feature"""
from concurrent import futures
import grpc
import communication.images_pb2
import communication.images_pb2_grpc
import configuration
import features.images.operations


class ImagesServicer(communication.images_pb2_grpc.ImagesServicer):
    def get_image_url(self, request, context):
        message = communication.images_pb2.ImageResponse(image_url='url')
        return message


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    communication.images_pb2_grpc.add_ImagesServicer_to_server(ImagesServicer(), server=server)
    server.add_insecure_port(configuration.Config().images_grpc_server_host)
    server.start()
    server.wait_for_termination()
