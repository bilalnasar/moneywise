import React, { useState, useContext } from 'react';
import Context from '../../Context';
import styles from './index.module.scss'; 

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isRegistering, setIsRegistering] = useState(false);
  const { dispatch } = useContext(Context);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const endpoint = isRegistering ? '/register' : '/token';
    try {
      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username, password }),
        credentials: 'include',
      });
      const data = await response.json();
      if (response.ok) {
        if (!isRegistering) {
          dispatch({ type: 'SET_STATE', state: { jwtToken: data.access_token, username: username } });
        }
        setIsRegistering(false);
      } else {
        alert(data.detail || 'An error occurred');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('An error occurred. Please try again.');
    }
  };

  return (
    <div className={styles.loginContainer}>
      <div className={styles.loginBox}>
        <h2 className={styles.loginTitle}>
          {isRegistering ? 'Moneywise' : 'Moneywise'}
        </h2>
        <form onSubmit={handleSubmit}>
          <div className={styles.inputField}>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Username"
              required
            />
          </div>
          <div className={styles.inputField}>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              required
            />
          </div>
          <button type="submit" className={styles.loginButton}>
            {isRegistering ? 'Register' : 'Login'}
          </button>
        </form>
        <button onClick={() => setIsRegistering(!isRegistering)} className={styles.switchButton}>
          {isRegistering ? 'Switch to Login' : 'Switch to Register'}
        </button>
      </div>
    </div>
  );
};

export default Login;