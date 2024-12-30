from concurrent import futures
import logging

import grpc
import schema_pb2
import schema_pb2_grpc


matrix=[]
m=-1
n=-1
with open("input.txt", 'r') as file:
    m,n=map(int, file.readline().split())
    for i in range(n):
        row=file.readline().split()
        matrix.append(row)

x=0
y=0
score=0
health=3
remaining_spells=3

class All_Services(schema_pb2_grpc.All_ServicesServicer):
    def initrpc(self, request, context):
        global m,n
        global matrix
        global x,y
        global score
        global health
        global remaining_spells
        with open("input.txt", 'r') as file:
            m,n=map(int, file.readline().split())
            for i in range(n):
                row=file.readline().split()
                matrix.append(row)
        x=0
        y=0
        score=0
        health=3
        remaining_spells=3
        return schema_pb2.RegisterMoveReply(status="Success")

    def GetLabyrinthInfo(self, request, context):
        return schema_pb2.GetLabyrinthInfoReply(width=m,height=n)

    def GetPlayerStatus(self, request, context):
        return schema_pb2.GetPlayerStatusReply(player_score=score,player_health=health,player_x=x,player_y=y,spells=remaining_spells)
    
    def RegisterMove(self, request, context):
        global x,y,health,score
        nx=0
        ny=0
        if request.direction=='N':
            nx=-1
        elif request.direction=='S':
            nx=1
        elif request.direction=='E':
            ny=1
        elif request.direction=='W':
            ny=-1
        else:
            nx=-x-1
            ny=-y-1
        x+=nx
        y+=ny
        if x<0 or x>=m or y<0 or y>=n or matrix[x][y]=='w':
            x-=nx
            y-=ny
            health-=1
            if health==0:
                return schema_pb2.RegisterMoveReply(status="death")
            return schema_pb2.RegisterMoveReply(status="Failure")
            

        if matrix[x][y]=='c':
            score+=1
            matrix[x][y]='.'

        if x==m-1 and y==n-1:
            return schema_pb2.RegisterMoveReply(status="Victory")

        return schema_pb2.RegisterMoveReply(status="Success")             

    def Revelio(self, request, context):
        global remaining_spells
        if remaining_spells==0:
            return schema_pb2.RevelioReply(revealed_x=[],revealed_y=[])
        remaining_spells-=1
        r_x=[]
        r_y=[]
        for i in range(max(0,request.x-1),min(request.x+2,m)):
            for j in range(max(0,request.y-1),min(request.y+2,n)):
                if matrix[i][j]==request.tiletype:
                    r_x.append(i)
                    r_y.append(j)
        return schema_pb2.RevelioReply(revealed_x=r_x,revealed_y=r_y)

    def Bombarda(self, request, context):
        global remaining_spells
        if remaining_spells==0:
            return schema_pb2.BombardaReply(status="No spells remaining")
        remaining_spells-=1
        for i in range(3):
            matrix[request.x[i]][request.y[i]]='.'
        return schema_pb2.BombardaReply(status="Success")

def serve():
    port = "50051"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    schema_pb2_grpc.add_All_ServicesServicer_to_server(All_Services(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    serve()