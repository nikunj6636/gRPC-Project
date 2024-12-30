package main

// Online doc project learning: anything big can be accomplished by just breaking very large
// task into very small taks and approaching step by step... not skipping any one step

// Learning: consider gRPC as an abstraction (1st computer science princile) and write code
// don't go in deep understanding of how gRPC code works

// Apply Mutex lock at client and server to handle simultaneous changes in both client.go and
// server.go file

// Make an in memory file in the server and a permanent storage

import (
	"fmt"
	"log"
	"net"
	"os"
	"syscall"
	"os/signal"

	"google.golang.org/grpc"
	pb "document/proto"
)

const filePath = "./server/file.txt"

type documentServer struct {
	pb.UnimplementedLiveDocumentServer // implement this server struct
	clients map[string]pb.LiveDocument_SyncDocumentServer
	numClients int
	text string // in memory file stores in the server
}

// handles empty string and any character
func (s* documentServer) applyChange(change *pb.DocumentChange){
	pos := int(change.Position)
	if change.Change == ""{ // delete char
		s.text = s.text[:pos-1] + s.text[pos:]
	}else{
		s.text = s.text[:pos] + change.Change + s.text[pos:]
	}
}

// Init the documentServer object
func createServer() *documentServer {
	// reading contents of database:
	data, err := os.ReadFile(filePath)
	if err != nil {
		log.Fatalf("Error opening file %v", err)
	}
	
	s := &documentServer{text: string(data), numClients: 0, clients: make(map[string]pb.LiveDocument_SyncDocumentServer)} 
	return s
}

// NOTE: fxn call is on documentServer object
func (s *documentServer) SyncDocument(stream pb.LiveDocument_SyncDocumentServer) error {

	clientId := fmt.Sprintf("Client-%d", s.numClients)
	s.clients[clientId] = stream
	stream.Send(&pb.DocumentChange{Change: s.text, Position: 0, ClientId: "server"})
	s.numClients++
	defer delete(s.clients, clientId) // when client disconnects
	
	for {
		change, err := stream.Recv() // blocking fxn call
		if err != nil {
			return err
		}

		// adding clientId and making change in server
		change.ClientId = clientId
		s.applyChange(change)
		
		// broadcasting changes to multiple clients
		for client, clientStream  := range s.clients {
			if client != clientId{
				go clientStream.Send(change) // non blocking call
			}
		}
	}
}

func main() {
	port := 50051
	lis, err := net.Listen("tcp", fmt.Sprintf("localhost:%d", port))
	if err != nil {
		log.Fatalf("failed to listen on port %d: %v", port, err)
	}else{
		fmt.Printf("Listening on port: %d\n", port)
	}

	var opts []grpc.ServerOption
	grpcServer := grpc.NewServer(opts...)

	s := createServer()
	pb.RegisterLiveDocumentServer(grpcServer, s)

	term := make(chan os.Signal, 1)
	// relay os.Signal to the channel, instead of creating interrupts by Signals
	signal.Notify(term, syscall.SIGTERM, syscall.SIGINT) 

	go func() { // go routine
		if err := grpcServer.Serve(lis); err != nil {
			term <- syscall.SIGINT // to terminate the program in case of err
		}
	}()

	<- term // block unitl signal is received
	
	grpcServer.GracefulStop() // stop the server
	os.WriteFile(filePath, []byte(s.text), 0644)
}