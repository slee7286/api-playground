from concurrent import futures

import grpc

import user_pb2
import user_pb2_grpc


class UserService(user_pb2_grpc.UserServiceServicer):

    def GetUser(self, request, context):
        return user_pb2.UserResponse(
            user_id=request.user_id,
            name="Alice",
            email="alice@example.com",
        )


server = grpc.server(
    futures.ThreadPoolExecutor(max_workers=10)
)

user_pb2_grpc.add_UserServiceServicer_to_server(
    UserService(),
    server,
)

server.add_insecure_port("[::]:50051")
server.start()

print("gRPC server running on port 50051")

server.wait_for_termination()