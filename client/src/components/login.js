import React, { useState } from "react";
import "./login.css";
import { useAuth } from "./auth";
import { useNavigate } from "react-router-dom";


const LoginForm =()=>{
    const [popupStyle,showPopup]=useState("hide");
    const [user,setUser]=useState()
    // const [password,setPassword]=useState('');
    const popup = ()=>{
        showPopup("login-popup")
        setTimeout(()=>showPopup("hide"),3000);
    }
    const auth = useAuth()
    const navigate= useNavigate();
    const handleLogin=()=>{
        auth.login(user);
        // console.log(user);
      
        navigate('/home');

        
    }
    return (
        <div className="page">
        <div className="cover">
        <h1>Login</h1>
            <input type="text" placeholder="username" onChange={(e)=>setUser(e.target.value)}/>
        <input type="password" placeholder="password" />
        <div className="login-btn" onClick={handleLogin}>Login</div>
        <p className="text">Or Login Using</p>
        <div className="alt-login">
            <div className="google"></div>
        </div>

        <div className={popupStyle}>
            <h3>Login Failed</h3>
            <p>Username or Password Incorrect</p>
        </div>
        </div>
        
        </div>
    )
}
export default LoginForm;