from concurrent import futures
import logging
import grpc
import knearest_pb2
import knearest_pb2_grpc

import numpy as np
from sklearn.neighbors import NearestNeighbors
import threading


class NearestNeighborServicer(knearest_pb2_grpc.NearestNeighborServicer):

    def __init__(self):
        self.num_points = 1000
        range = 1000 # data points loaded randomly.
        self.points = np.random.randint(-range, range+1, size=(self.num_points, 2))
        self.nn = NearestNeighbors(metric='euclidean')
        self.nn.fit(self.points)

    
    def GetKNearest(self, request, context):
        query_point = np.array([[request.P.x, request.P.y]])
        k = request.k
        distances, indices = self.nn.kneighbors(query_point, n_neighbors=k)

        response = knearest_pb2.KNearestResponse()
        for i in range(k):
            knearest_point = response.points.add()
            knearest_point.P.x = int(self.points[indices[0][i]][0])
            knearest_point.P.y = int(self.points[indices[0][i]][1])
            knearest_point.distance = float(distances[0][i])

        return response


def serve(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    knearest_pb2_grpc.add_NearestNeighborServicer_to_server(
        NearestNeighborServicer(), server
    )
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"Server started, listening on port {port}")
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()

    ports = [50051, 50052, 50053]
    threads = []

    for port in ports:
        thread = threading.Thread(target=serve, args=(port,))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
