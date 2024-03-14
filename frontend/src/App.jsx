import React, { useEffect } from "react";
import { HashRouter, Routes, Route, Navigate } from "react-router-dom";
import Sidebar from "./sidebar.jsx";
import Header from "./header.jsx";
import Content from "./content.jsx";
import LoginPage from "./loginpage.jsx";
import SignUpPage from "./signuppage.jsx";
import { NextUIProvider } from "@nextui-org/react";
import { UserProvider, useUser } from "./UserContext"; // Assuming UserContext.js is in the same directory

function App() {
  useEffect(() => {
    document.body.style.backgroundColor = "orange";
  }, []);

  return (
    <UserProvider>
      {" "}
      {/* Wrap the application with UserProvider */}
      <HashRouter>
        <NextUIProvider>
          <Layout />
        </NextUIProvider>
      </HashRouter>
    </UserProvider>
  );
}

// Splitting the layout into a separate component for using useUser hook
function Layout() {
  const { user, setUser } = useUser(); // Use useUser hook

  const handleLogin = (user) => {
    setUser(user); // Update login status with the user info
  };

  const handleLogout = () => {
    setUser(null); // Clear user info on logout
  };

  return (
    <>
      {user && <Header onLogout={handleLogout} />}
      <div
        style={{
          display: "flex",
          paddingTop: user ? "100px" : "0",
          minHeight: "100vh",
        }}
      >
        {user && (
          <div style={{ width: "22%" }}>
            <Sidebar />
          </div>
        )}
        <div style={{ flex: 1 }}>
          <Routes>
            {user ? (
              <>
                <Route path="/:ticker" element={<Content />} />
                <Route path="/summary" element={<Content />} />
                <Route path="/" element={<Navigate replace to="/summary" />} />
              </>
            ) : (
              <>
                <Route
                  path="/login"
                  element={<LoginPage onLogin={handleLogin} />}
                />
                <Route
                  path="/register"
                  element={<SignUpPage onRegister={handleLogin} />}
                />
                <Route path="/*" element={<Navigate replace to="/login" />} />
              </>
            )}
          </Routes>
        </div>
      </div>
    </>
  );
}

export default App;
