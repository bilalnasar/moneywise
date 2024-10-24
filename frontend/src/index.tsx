import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { MoneywiseProvider } from "./Context";

ReactDOM.render(
  <React.StrictMode>
    <BrowserRouter>
      <MoneywiseProvider>
        <App />
      </MoneywiseProvider>
    </BrowserRouter>
  </React.StrictMode>,
  document.getElementById("root")
);
