import React, {useState, useEffect} from 'react';
import './App.css';

function App() {
  const [clientId, setClienId] = useState(
    Math.floor(new Date().getTime() / 1000)
  );
    const [websock,setWebsock]=useState();
    const [message,setMessage]= useState([]);
    const [messages,setMessages]= useState([]);
      useEffect(()=>{
        const url = "ws://localhost:8000/ws/"+clientId;
        const ws = new WebSocket(url);
        ws.onopen=(e)=>{
          ws.send("connect");
        };
        ws.onmessage=(e)=>{
          const message=JSON.parse(e.data);
          setMessages([...messages,message]);
        };
        setWebsock(ws);
        return ()=>ws.close();
      },[]);

      const sendMessage=()=>{
        websock.send(message);
        websock.onmessage=(e)=>{
          const message= JSON.parse(e.data);
          setMessages([...messages,message]);
        };
        setMessage([]);
      };
  return (
    <div className = "container">
      <h1>Chat App</h1>
      <h2>Client Id: {clientId} </h2>
      <div className="chat-container">
        <div className="chat">
        {messages.map((value,index)=>{
          if(value.clientId===clientId){
            return(
              <div key={index} className='sender-message-container'>
            <div  className="sender-message">
              <p className="client">Client Id :{clientId} </p>
              <p className ="message"> {value.message}</p>
            </div>
            </div>
            );
          }else{
            return(
              <div  key = {index} className="receiver-message-container">
            <div className="receiver-message">
              <p className ="client">Client Id : {clientId}</p>
              <p className ="message">{value.message}</p>
            </div>
          </div>
            );
          }
        })}

          
        </div>
      <div className ="input-container">
        <input className="input-chat" type="text" placeholder="Send message "
          onChange={(e)=>setMessage(e.target.value)}
          value={message}
        
        ></input>
        <button className ="submit"  onClick={sendMessage}>Send </button>
      </div>
      </div>
    </div>
  );
}

export default App;

