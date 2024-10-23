import React, { useEffect, useContext, useCallback } from "react";

import Header from "./Components/Headers";
import Context from "./Context";
import Login from "./Components/Login";
import Dashboard from "./Components/Dashboard";
import { Route, Routes, Navigate } from "react-router-dom";

import styles from "./App.module.scss";

const App = () => {
  const { linkSuccess, isPaymentInitiation, dispatch, jwtToken } =
    useContext(Context);

  const getInfo = useCallback(async () => {
    const response = await fetch("/api/info", { 
      method: "POST",
      headers: {
        'Authorization': `Bearer ${jwtToken}`,
      },
    });
    if (!response.ok) {
      dispatch({ type: "SET_STATE", state: { backend: false } });
      return { paymentInitiation: false };
    }
    const data = await response.json();
    const paymentInitiation: boolean =
      data.products.includes("payment_initiation");
    dispatch({
      type: "SET_STATE",
      state: {
        products: data.products,
        isPaymentInitiation: paymentInitiation,
      },
    });
    return { paymentInitiation };
  }, [dispatch, jwtToken]);

  const generateToken = useCallback(
    async (isPaymentInitiation) => {
      const path = isPaymentInitiation
        ? "/api/create_link_token_for_payment"
        : "/api/create_link_token";
      const response = await fetch(path, {
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
        dispatch({ type: "SET_STATE", state: { linkToken: data.link_token } });
      }
      localStorage.setItem("link_token", data.link_token);
    },
    [dispatch]
  );

  useEffect(() => {
    if (jwtToken) {
      const init = async () => {
        const { paymentInitiation } = await getInfo();
        if (window.location.href.includes("?oauth_state_id=")) {
          dispatch({
            type: "SET_STATE",
            state: {
              linkToken: localStorage.getItem("link_token"),
            },
          });
          return;
        }
        generateToken(paymentInitiation);
      };
      init();
    }
  }, [dispatch, generateToken, getInfo, jwtToken]);

  if (!jwtToken) {
    return <Login />;
  }

  return (
    <div className={styles.App}>
      <Header />
      <div className={styles.container}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </div>
    </div>
  );
};

export default App;