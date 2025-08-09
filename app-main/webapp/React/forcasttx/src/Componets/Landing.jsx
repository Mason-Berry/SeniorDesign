import { useNavigate } from 'react-router-dom';
import { useEffect } from "react";
import "../styles/landing.css";

function Landing() {
    const navigate = useNavigate();

    useEffect(() => {
        // Add landing class on mount
        document.body.classList.add("landing");
        // Remove it on unmount
        return () => document.body.classList.remove("landing");
    }, []);

    useEffect(() => {
        const timer = setTimeout(() => navigate("/login"), 3000);
        return () => clearTimeout(timer);
    }, [navigate]);

    return (
        <div className="landing-container">
           
            <div className="landing-welcome-text">
                ForecastTX.
            </div>
        </div>
    );
}

export default Landing;