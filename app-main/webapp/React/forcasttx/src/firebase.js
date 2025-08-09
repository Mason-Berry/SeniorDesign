// src/firebase.js

import { initializeApp } from "firebase/app";
import {
  getAuth,
  GoogleAuthProvider,
  OAuthProvider,
  connectAuthEmulator,
} from "firebase/auth";


const firebaseConfig = {
  apiKey: "AIzaSyC4zToODBT7YqjdyuSOSBTdLxvCnFHVBRI",
  authDomain: "argon-edge-455015-q8.firebaseapp.com",
  projectId: "argon-edge-455015-q8",
  storageBucket: "argon-edge-455015-q8.firebasestorage.app",
  messagingSenderId: "553337662428",
  appId: "1:553337662428:web:d8435981f577c26d2bfd19",
  measurementId: "G-FN4VB5F5XQ"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Auth
const auth = getAuth(app);

const useAuthEmulator =
  window.location.hostname === "localhost" &&
  process.env.REACT_APP_USE_AUTH_EMULATOR === "true";

if (useAuthEmulator) {
  connectAuthEmulator(auth, "http://localhost:9099");
}

// Google and Microsoft Providers
const googleProvider = new GoogleAuthProvider();
const microsoftProvider = new OAuthProvider("microsoft.com");


export {
  app,
  auth,
  googleProvider,
  microsoftProvider
};





