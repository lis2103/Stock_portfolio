// main.tsx or main.jsx
import React from "react";
import * as ReactDOM from "react-dom/client";
import { NextUIProvider } from "@nextui-org/react";
import App from "./App.jsx";
import "./index.css";

ReactDOM.createRoot.render(
  <React.StrictMode>
    <NextUIProvider>
      <main className="dark text-foreground bg-background">
        <App />
      </main>
    </NextUIProvider>
  </React.StrictMode>
);
