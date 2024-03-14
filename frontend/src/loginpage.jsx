import React, { useState } from "react";
import { Button } from "@nextui-org/react";
import { Link, useNavigate } from "react-router-dom";
import { useUser } from "./UserContext"; // Import useUser hook from your UserContext file

const LoginPage = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const { setUserData } = useUser(); // Use the setUserData function from context to update user state

  const handleSubmit = async (e) => {
    e.preventDefault();

    const loginDetails = { username, password };

    try {
      const response = await fetch(
        "https://mcsbt-integration-vr.ew.r.appspot.com/login",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(loginDetails),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to login");
      }

      const data = await response.json();
      console.log("Login successful:", data.message);

      setUserData({ username: username, id: data.userId }); // Update the user context with the logged-in user's data
      navigate("/summary"); // Redirect to the summary page
    } catch (error) {
      console.error("Login error:", error.message);
      setError(error.message); // Optionally update error state to display the message
      alert(error.message); // Display the error message to the user
    }
  };

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "left",
        alignItems: "center",
        height: "100vh",
      }}
    >
      <form
        onSubmit={handleSubmit}
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "0px",
          width: "300px",
          textAlign: "center",
        }}
      >
        <h2
          style={{ fontSize: "48px", margin: "0 0 15px 0", fontWeight: "1000" }}
        >
          WELCOME TO LISTOCK
        </h2>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username"
          style={{
            fontSize: "14px",
            borderRadius: "10px 10px 0 0", // Adjusted borderRadius
            border: "1px solid #ccc",
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
            fontSize: "20px",
            borderRadius: "1",
            border: "1px solid #ccc",
            borderTop: "1",
            padding: "10px",
            width: "100%",
          }}
        />
        <Button
          fullWidth
          auto
          type="continue"
          style={{
            borderRadius: "0 0 10px 10px",
            padding: "5px 10px",
            boxSizing: "border-box",
            color: "red",
            width: "100%", // Adjusted to full width for consistency
            height: "35px", // Adjusted height
            fontSize: "20px",
            borderTop: "0",
            border: "1px solid #ccc",
            marginTop: "-1px",
            disableAnimation: true,
          }}
        >
          continue
        </Button>
        <p style={{ color: "green", marginTop: "15px", fontSize: "13px" }}>
          Not registered? Register{" "}
          <Link
            to="/register"
            style={{ color: "inherit", textDecoration: "inherit" }}
          >
            <strong>here</strong>
          </Link>
          .
        </p>
      </form>
    </div>
  );
};

export default LoginPage;
