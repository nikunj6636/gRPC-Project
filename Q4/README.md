To generate code for gRPC run command(in directory Q4):
- using option go_package="./proto"
-   ```
    protoc --go_out=. --go-grpc_out=. proto/document.proto 
    ```

To run client code run command(in directory Q4):
```
go run client/client.go
```


To run server code run command(in directory Q4):
```
go run server/server.go
```


To run logger code run command(in directory Q4):
```
go run logger/logger.go
```

### Synchronization steps:
1. Server starts and loads the contents from "server/file.txt"
2. Client joins the server, enters the text editor (termbox library).
3. Client reads the keyboard inputs and changes local document.
4. Client sends local changes to server.
5. Server on receiving changes from a single client, broadcasts changes to other clients
6. Server also sends the changes to the logger progeam and changes file in memory.
7. When interrupt signal is sent server saves the file in disk from in memory and stops.