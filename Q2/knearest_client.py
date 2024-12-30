from __future__ import print_function

import logging
import knearest_pb2
import knearest_pb2_grpc
import grpc
import heapq

from concurrent.futures import ThreadPoolExecutor, as_completed


def queryServer(port, x, y, k):
    with grpc.insecure_channel(f"localhost:{port}") as channel:
        stub = knearest_pb2_grpc.NearestNeighborStub(channel)
        Point = knearest_pb2.Point(x=x, y=y)
        QueryPoint = knearest_pb2.QueryPoint(P = Point, k = k)
        kNearestPoints = stub.GetKNearest(QueryPoint)
        return kNearestPoints.points


def run(x, y, k):
    server_ports = [50051, 50052, 50053]

    kNearestPoints = []

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(queryServer, port, x, y, k) for port in server_ports]

        for future in as_completed(futures): # returns an iterator over objects with completed execution
            ServerResponse = future.result()
            for point in ServerResponse:
                print(point)
                heapq.heappush(kNearestPoints, (-point.distance, point.P.x, point.P.y))
                if len(kNearestPoints) > k: heapq.heappop(kNearestPoints)

    
    print("-------------- K Nearest Points In Reverse Order --------------")
    while kNearestPoints:
        _, x, y = heapq.heappop(kNearestPoints)
        print(x, y)


if __name__ == "__main__":
    logging.basicConfig()

    x = int(input("x: "))
    y = int(input("y: "))
    k = int(input("k: "))

    run(x, y, k)