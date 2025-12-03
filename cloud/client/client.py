import grpc
import cloudsecurity_pb2
import cloudsecurity_pb2_grpc
import nodes_pb2
import nodes_pb2_grpc

def login(stub):
    login = input("Enter username: ")
    pwd = input("Enter password: ")
    req = cloudsecurity_pb2.Request(login=login, password=pwd)
    res = stub.login(req)
    print("Login Response:", res.result)
    return login

def create_node(stub, user):
    node_type = input("Enter node type (small/medium/gpu): ")
    req = nodes_pb2.NodeRequest(user=user, node_type=node_type)
    res = stub.CreateNode(req)
    print(f"Node Result: {res.result}, Node ID: {res.node_id}")

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        auth_stub = cloudsecurity_pb2_grpc.UserServiceStub(channel)
        node_stub = nodes_pb2_grpc.NodeServiceStub(channel)

        user = login(auth_stub)
        create_node(node_stub, user)

if __name__ == "__main__":
    run()
