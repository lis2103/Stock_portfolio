import React, { createContext, useContext, useState } from "react";

const UserContext = createContext();

export const useUser = () => useContext(UserContext);

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  // Function to set user data including the ID
  const setUserData = (userData) => {
    setUser(userData);
  };

  return (
    <UserContext.Provider value={{ user, setUserData }}>
      {children}
    </UserContext.Provider>
  );
};
