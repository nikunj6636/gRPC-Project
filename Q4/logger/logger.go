// like a client which only listen for changes with that stream and prints those changes in a log file
package main

import (
	"fmt"
	"log"
	"context"
	"os"

	pb "document/proto"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

const filePath = "./logger/logs.txt"

func main() {

	// Init gRPC connection
	conn, err := grpc.NewClient("localhost:50051", grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("fail to dial: %v", err)
	}
	defer conn.Close()

	client := pb.NewLiveDocumentClient(conn)
	stream, err := client.SyncDocument(context.Background())
	if err != nil {
		log.Fatalf("client.SyncDocument failed: %v", err)
	}

	// Open the file for writing, create if it doesn't exist, truncate if it does.
	file, err := os.OpenFile(filePath, os.O_WRONLY|os.O_CREATE|os.O_APPEND, 0644)
	if err != nil {
		fmt.Println("Error opening file:", err)
		return
	}
	defer file.Close() // Ensure the file is closed when the function returns
	logger := log.New(file, "", log.LstdFlags)

	for{
		change, err := stream.Recv() // receives EOF error when server is closed
		if err != nil{
			log.Fatalf("stream.Recv(%v) failed: %v", change, err)
		}else{
			ch := change.Change
			if ch == "\n"{
				ch = "newline"
			}
			logger.Printf( "client: %s, change: %s, position: %d\n", change.ClientId, ch, change.Position)
		}
	}
}