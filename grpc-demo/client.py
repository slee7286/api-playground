import grpc

import user_pb2
import user_pb2_grpc


with grpc.insecure_channel("localhost:50051") as channel:

    stub = user_pb2_grpc.UserServiceStub(channel)

    response = stub.GetUser(
        user_pb2.GetUserRequest(user_id=123),
        timeout=5,
    )

    print(response.name)
    print(response.email)