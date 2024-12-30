package main

// Idea is to build the complete code on your own!, by breaking big problm into small
// subproblems and solving them! with the use of AI, whic is the real dev skills required!

import (
	"log"
	term "github.com/nsf/termbox-go"

	"context"
	pb "document/proto"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)
const color = term.ColorDefault
const defaultString = "abc"

type documentClient struct{
	text string
	position int
}

// handles empty string and any character
func (c* documentClient) applyChange(change *pb.DocumentChange){
	pos := int(change.Position)
	if change.Change == ""{ // delete char
		c.text = c.text[:pos-1] + c.text[pos:]
		if pos <= c.position{
			c.position--
		}
	}else{
		c.text = c.text[:pos] + change.Change + c.text[pos:]
		if pos <= c.position{
			c.position += len(change.Change)
		}
	}
}

// defining the interface on documentClient, assumption: position <= len(text) follows text
func (c *documentClient) renderDocument(){ 
	term.Clear(term.ColorDefault, term.ColorDefault)
	x, y := 0, 0
	cursorX, cursorY := 0, 0

	for i, ch := range c.text {
		term.SetCell(x, y, ch, color, color)
		if i == c.position{
			cursorX, cursorY = x, y
		}

		if ch == '\n'{
			y++
			x=0
		}else{
			x++
		}
	}

	if c.position == len(c.text){
		cursorX, cursorY = x, y
	}

	term.SetCursor(cursorX, cursorY) // x and y coordinates are opposite here
	term.Flush()
}

func main() {

	// Init termbox
	err := term.Init()
	if err != nil {
        panic(err)
    }
	defer term.Close()

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

	// Init document: with any empty string
	c := &documentClient{text: "", position: 0}

	// concurrently listening for changes
	go func() {	
		for{
			change, err := stream.Recv()
			if err != nil{
				log.Fatalf("stream.Recv(%v) failed: %v", change, err)
			}
			c.applyChange(change)
			c.renderDocument()
		}
    }()

	// listening changes from keyboard and sending changes
	keyPressListenerLoop:
    for {
        switch ev := term.PollEvent(); ev.Type { // blocking fxn call
        case term.EventKey:
			ch := defaultString

            switch ev.Key {
				case term.KeyEsc, term.KeyCtrlC:
					break keyPressListenerLoop
				case term.KeyArrowLeft:
					if c.position > 0{
						c.position--
					}
				case term.KeyArrowRight:
					if c.position < len(c.text){
						c.position++
					}
				case term.KeyBackspace2, term.KeyBackspace:
					if c.position > 0{
						ch = ""
					}
				case term.KeyEnter:
					ch = "\n"
				case term.KeySpace:
					ch = " "
				default:
					if ev.Ch != 0 { // Valid char pressed!
						ch = string(rune(ev.Ch))
					}			
            }
			
			// If document is changed!, apply changes and send changes to the server!
			if ch != defaultString{
				change := &pb.DocumentChange{Change: ch, Position: int32(c.position)}

				if err := stream.Send(change); err != nil { // returns err when channel is closed!
					log.Fatalf("stream.Send(%v) failed: %v", change, err)
				}
				c.applyChange(change)
			}

			c.renderDocument() // re-render document

        case term.EventError:
            panic(ev.Err)
        }
    }
}