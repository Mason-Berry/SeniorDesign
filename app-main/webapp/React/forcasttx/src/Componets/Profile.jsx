import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { signOut } from 'firebase/auth';
import { auth } from '../firebase'; 
import '../styles/Profile.css'; // Ensure you have the styles
import userSVG from '../assets/user.svg';

const Profile = () => {
  const navigate = useNavigate();
  const [showLogout, setShowLogout] = useState(false);

  const user = auth.currentUser;

  const handleLogout = async () => {
    try {
      await signOut(auth);
      navigate('/'); 
    } catch (error) {
      console.error("Error signing out:", error);
    }
  };

  const toggleLogout = () => {
    setShowLogout(!showLogout);
  };

  return (
    <div className="profile-container">
      <div className="profile-info" onClick={toggleLogout}>
        <img
          src={user?.photoURL || userSVG}
          alt="User"
          className="profile-pic"
        />
        <span className="profile-email">
          {user?.email || "User"}
        </span>
      </div>
      {showLogout && (
        <button className="logout-button" onClick={handleLogout}>
          Logout
        </button>
      )}
    </div>
  );
};

export default Profile;