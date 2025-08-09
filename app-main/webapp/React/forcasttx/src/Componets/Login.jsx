import { useNavigate } from 'react-router-dom';
import { auth, googleProvider, microsoftProvider } from '../firebase';
import { signInWithPopup, signOut } from "firebase/auth";
import "../styles/login.css";

// Hardcoded allowed emails list ( we can change it by using functions but we need to pay for it.)
const allowedEmails = [
  "kevinsimbakwira@gmail.com",
  "kxs7244@mavs.uta.edu.",
  "kevinsimbakwira@outlook.com",
  "mason.berry9515@gmail.com",
  "noesanchez00000@gmail.com",
 "kxp6113@mavs.uta.edu",
  "kristal.phommalay@gmail.com"
];

function Login() {
  const navigate = useNavigate();

  const handleLogin = async (provider) => {
    try {
      const result = await signInWithPopup(auth, provider);
      const email = result.user.email;

      if (allowedEmails.includes(email)) {
        navigate("/dashboard");
      } else {
        alert("Access denied. You are not authorized.");
        await signOut(auth);
      }
    } catch (error) {
      console.error("Error during login:", error);
      alert("Login failed. Please try again.");
    }
  };

  return (
    <div className="login-container">
      <div className="login-subtitle">ForecastTX</div>
      <h2 className="login-title">Login</h2>
      <div className="login-form">
        <button onClick={() => handleLogin(googleProvider)} className="login-btn" style={{marginBottom: "10px"}}>
          Sign in with Google
        </button>
        <button onClick={() => handleLogin(microsoftProvider)} className="login-btn">
          Sign in with Microsoft
        </button>
      </div>
    </div>
  );
}

export default Login;