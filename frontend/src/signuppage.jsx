import React, { useState } from "react";
import { Button } from "@nextui-org/react";
import { Link, useNavigate } from "react-router-dom";
import { useUser } from "./UserContext"; // Import useUser hook

const RegisterPage = () => {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const { setUserData } = useUser(); // Use the setUserData function from the context
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate form inputs
    if (!username || !email || !password || !confirmPassword) {
      alert("Please fill in all the fields.");
      return;
    }
    if (password !== confirmPassword) {
      alert("Passwords do not match.");
      return;
    }

    try {
      const response = await fetch(
        "https://mcsbt-integration-416413.lm.r.appspot.com/register",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ username, email, password }),
        }
      );

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Failed to register");
      }

      console.log("User registered successfully:", data.message);
      setUserData({ username: username, id: data.userId }); // Update the user context with the registered user's data
      navigate("/summary"); // Redirect to the summary page upon successful registration
    } catch (error) {
      alert(error.message); // Display registration error message
    }
  };

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
      }}
    >
      <form
        onSubmit={handleSubmit}
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "0px", // Controls the distance between elements
          width: "300px", // Adjust the form width here
          textAlign: "center", // Ensures text elements inside the form are centered
        }}
      >
        <h2
          style={{
            fontSize: "24px",
            margin: "0 0 15px 0",
            fontWeight: "600",
          }}
        >
          Stock Portfolio Tracker
        </h2>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username"
          style={{
            fontSize: "14px",
            borderRadius: "10px 10px 0 0", // Adjusted borderRadius for the top input
            border: "1px solid #ccc",
            padding: "10px",
            width: "100%",
          }}
        />
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          style={{
            fontSize: "14px",
            borderRadius: "0", // Straight corners for middle inputs
            border: "1px solid #ccc",
            borderTop: "0", // Remove top border to eliminate space
            padding: "10px",
            width: "100%",
          }}
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          style={{
            fontSize: "14px",
            borderRadius: "0", // Straight corners
            border: "1px solid #ccc",
            borderTop: "0", // Remove top border
            padding: "10px",
            width: "100%",
          }}
        />
        <input
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          placeholder="Confirm Password"
          style={{
            fontSize: "14px",
            borderRadius: "0 0 0 0", // Adjusted borderRadius for the bottom input
            border: "1px solid #ccc",
            borderTop: "0", // Remove top border
            padding: "10px",
            width: "100%",
          }}
        />
        <Button
          fullWidth
          auto
          type="submit"
          style={{
            borderRadius: "0 0 10px 10px", // Rounded corners for the button if separate from inputs
            padding: "10px",
            boxSizing: "border-box",
            width: "100%", // Adjusted to full width for consistency
            height: "35px", // Adjusted height
            fontSize: "14px",
            border: "1px solid #ccc", // Apply border styling consistently
            marginTop: "-1px", // Space between last input and button, adjust as needed
          }}
        >
          Register
        </Button>
        <p style={{ marginTop: "15px", fontSize: "13px" }}>
          Already registered? Login{" "}
          <Link
            to="/login"
            style={{ color: "inherit", textDecoration: "none" }}
          >
            <strong>here</strong>
          </Link>
          .
        </p>
      </form>
    </div>
  );
};

export default RegisterPage;
