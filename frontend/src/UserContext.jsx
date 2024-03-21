import React, { createContext, useContext, useState } from "react";

const UserContext = createContext();

export const useUser = () => useContext(UserContext);

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [reloadTrigger, setReloadTrigger] = useState(false); // Added state for reload trigger

  // Function to set user data including the ID
  const setUserData = (userData) => {
    setUser(userData);
  };

  // Function to toggle the reload trigger
  const triggerReload = () => setReloadTrigger((prev) => !prev);

  return (
    <UserContext.Provider
      value={{ user, setUserData, reloadTrigger, triggerReload }}
    >
      {children}
    </UserContext.Provider>
  );
};
