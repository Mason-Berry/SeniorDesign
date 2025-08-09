
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

import Login from "./Componets/Login";
import CreateAccount from "./Componets/CreateAccount";
import Landing from "./Componets/Landing";
import Dashboard from "./Componets/Dashboard";

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Landing/>} />
                <Route path="/login" element={<Login/>} />
                <Route path="/create-account" element={<CreateAccount/>} />
                <Route path="/dashboard" element={<Dashboard/>} />
            </Routes>
        </Router>
    );
}

export default App;
