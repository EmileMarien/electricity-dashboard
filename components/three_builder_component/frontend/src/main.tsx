import React from "react";
import ReactDOM from "react-dom/client";
import { withStreamlitConnection } from "streamlit-component-lib";
import { ThreeBuilder } from "./ThreeBuilder";

const Connected = withStreamlitConnection(ThreeBuilder);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Connected />
  </React.StrictMode>
);
