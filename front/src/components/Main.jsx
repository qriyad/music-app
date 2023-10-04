import React from 'react'
import "./Main.css"
import { Button } from 'antd';
import img from "./image5.png"
const Main = () => {
    return (
        <div className='div'>
            <div className='Nav'>
                <div className='center'>
                    <p>Music Platform</p>
                </div>
                <div className="links">
                    <p>Musics</p>
                    <p>PlayList</p>
                    <p>Favorites</p>
                </div>
                <div className="link">
                    <Button className='Button' style={{ "background": "rgb(109, 48, 109)", "color": "white" }}>Sign up</Button>
                    <Button className='Button' style={{ "background": "rgb(109, 48, 109)", "color": "white" }}>Sign in</Button>

                </div>
            </div>
            <div className="header">
                <div className="text">
                    <p>Music Platform for</p>
                    <p>Digital Music for fans.</p>
                </div>
                <div className="text2">
                    <img src={img} alt="" />
                </div>
            </div>
        </div>

    )
}

export default Main