import grpc
from concurrent import futures
import cloudsecurity_pb2_grpc
import nodes_pb2_grpc
from auth_service import UserServiceSkeleton
from node_service import NodeServiceSkeleton

def run():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # register authentication service
    cloudsecurity_pb2_grpc.add_UserServiceServicer_to_server(UserServiceSkeleton(), server)

    # register node service
    nodes_pb2_grpc.add_NodeServiceServicer_to_server(NodeServiceSkeleton(), server)

    server.add_insecure_port('[::]:50051')
    print("Starting Unified Cloud Server on port 50051 ...")
    server.start()
    print("Server is running.")
    server.wait_for_termination()

if __name__ == '__main__':
    run()
