import React, { useEffect, useContext, useCallback } from "react";
import Header from "./Components/Headers";
import Context from "./Context";
import Login from "./Components/Login";
import Dashboard from "./Components/Dashboard";
import { Route, Routes, Navigate } from "react-router-dom";
import styles from "./App.module.scss";
import Sidebar from "./Components/Sidebar";


const App = () => {
  const { linkSuccess, dispatch, jwtToken, accessToken } = useContext(Context);

  const getInfo = useCallback(async () => {
    const response = await fetch("/api/info", { 
      method: "POST",
      headers: {
        'Authorization': `Bearer ${jwtToken}`,
      },
    });
    if (!response.ok) {
      dispatch({ type: "SET_STATE", state: { backend: false } });
      return;
    }
    const data = await response.json();
    dispatch({
      type: "SET_STATE",
      state: {
        products: data.products,
        accessToken: data.access_token,
      },
    });
  }, [dispatch, jwtToken]);

  const generateToken = useCallback(async () => {
    const response = await fetch("/api/create_link_token", {
      method: "POST",
    });
    if (!response.ok) {
      dispatch({ type: "SET_STATE", state: { linkToken: null } });
      return;
    }
    const data = await response.json();
    if (data) {
      if (data.error != null) {
        dispatch({
          type: "SET_STATE",
          state: {
            linkToken: null,
            linkTokenError: data.error,
          },
        });
        return;
      }
      dispatch({ type: "SET_STATE", state: { linkToken: data.link_token, linkSuccess: true } });
    }
    localStorage.setItem("link_token", data.link_token);
  }, [dispatch]);

  useEffect(() => {
    if (jwtToken) {
      const init = async () => {
        await getInfo();
        if (window.location.href.includes("?oauth_state_id=")) {
          dispatch({
            type: "SET_STATE",
            state: {
              linkToken: localStorage.getItem("link_token"),
            },
          });
          return;
        }
        generateToken();
      };
      init();
    }
  }, [dispatch, generateToken, getInfo, jwtToken]);

  if (!jwtToken) {
    return <Login />;
  }

  return (
    <div className={styles.App}>
      <Sidebar />
      <div className={styles.mainContent}>
        {!accessToken ? (
          <Header />
        ) : (
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        )}
      </div>
    </div>
  );
};

export default App;