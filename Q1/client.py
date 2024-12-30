from __future__ import print_function

import logging

import grpc
import schema_pb2
import schema_pb2_grpc

def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub=schema_pb2_grpc.All_ServicesStub(channel)
        response = stub.initrpc(schema_pb2.Emptyreq())
    while True:
        print("Choose the operation you want to perform ")
        print("1. GetLabyrinthInfo")
        print("2. GetPlayerStatus")
        print("3. RegisterMove")
        print("4. Revelio")
        print("5. Bombarda")
        inp=int(input())
        with grpc.insecure_channel("localhost:50051") as channel:
            stub = schema_pb2_grpc.All_ServicesStub(channel)
            if inp==1:
                response = stub.GetLabyrinthInfo(schema_pb2.Emptyreq())
                print("Width: ",response.width)
                print("Height: ",response.height)
            elif inp==2:
                response = stub.GetPlayerStatus(schema_pb2.Emptyreq())
                print("Player Score: ",response.player_score)
                print("Player Health: ",response.player_health)
                print("Spells: ",response.spells)    
                print(f"Player position: ({response.player_x},{response.player_y})")
            elif inp==3:    
                print("Enter the direction you want to move in (N,S,E,W)")
                direction=input()
                response = stub.RegisterMove(schema_pb2.RegisterMoveRequest(direction=direction))
                print("Status: ",response.status)
                if(response.status=="Victory" or response.status=="death"):
                    break

            elif inp==4:
                print("Enter the x and y coordinates of the target tile in x y format")
                inp=input()
                x,y = map(int, inp.split())
                print("Enter the tile type (c/w/.) ")
                tiletype=input()
                response = stub.Revelio(schema_pb2.RevelioRequest(x=x,y=y,tiletype=tiletype))
                for i in range(len(response.revealed_x)):
                    print("Revealed x,y: ",response.revealed_x[i],response.revealed_y[i])
                    
            elif inp==5:
                x1,y1=map(int,input("Enter x1 y1 ").split())
                x2,y2=map(int,input("Enter x2 y2 ").split())
                x3,y3=map(int,input("Enter x3 y3 " ).split())
                response = stub.Bombarda(schema_pb2.BombardaRequest(x=[x1,x2,x3],y=[y1,y2,y3]))
                print("Status: ",response.status)
            else:
                print("Invalid input")

if __name__ == "__main__":
    logging.basicConfig()
    run()
