import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

// Your web app's Firebase configuration
// For educational/demonstration purposes, using info from project
const firebaseConfig = {
  apiKey: "AIzaSyA9ZnVnKfCmoAcHmtJnoKqFYB0rg6O8sko",
  authDomain: "npsb-smart-ticketing.firebaseapp.com",
  projectId: "npsb-smart-ticketing",
  storageBucket: "npsb-smart-ticketing.firebasestorage.app",
  messagingSenderId: "705629174032",
  appId: "1:705629174032:web:99a24285f6869f3e924d95",
  measurementId: "G-Y356X54ZHN"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app, "tickets");
export default app;
