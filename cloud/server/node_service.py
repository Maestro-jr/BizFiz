import grpc
from concurrent import futures
import nodes_pb2
import nodes_pb2_grpc
import uuid

class NodeServiceSkeleton(nodes_pb2_grpc.NodeServiceServicer):
    def CreateNode(self, request, context):
        print(f"New node request: {request}")

        # MVP NODE CREATION LOGIC
        node_id = str(uuid.uuid4())[:8]

        # Simulated VM creation (no real cloud provider yet)
        print(f"Node created: {node_id} for user {request.user}")

        return nodes_pb2.NodeResponse(
            result="Node created successfully",
            node_id=node_id
        )
