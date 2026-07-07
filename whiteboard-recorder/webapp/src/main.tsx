import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

// 让 Excalidraw 从本地 node_modules 加载资源，避免 unpkg CDN 失败
(window as any).EXCALIDRAW_ASSET_PATH = '/node_modules/@excalidraw/excalidraw/dist/';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
