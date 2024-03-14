// src/index.jsx
import "./index.css";

import React from "react";
import ReactDOM from "react-dom";
import "./index.css"; // Import the global stylesheet
import App from "./App";

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById("root")
);
