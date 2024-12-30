To run the code:

```
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. knearest.proto
```

Note: Here -I is used for importing .proto files in main.proto file

To check if server is running:
```
telnet localhost 50051
```

Run the Program:
```
python3 knearest_server.py
python3 knearest_client.py
```