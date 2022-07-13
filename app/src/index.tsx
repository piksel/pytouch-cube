import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { createRoot } from 'react-dom/client';

const ModeWrapper = process.env.STRICT_MODE === 'yes' ? React.StrictMode : React.Fragment;
const container = document.getElementById('root');
const root = createRoot(container!); 

root.render(
  <ModeWrapper>
    <App />
  </ModeWrapper>,
  
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
