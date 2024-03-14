// src/services/api.js

import axios from "axios";

const API_URL = process.env.REACT_APP_BACKEND_URL;

export const loginUser = async (username, password) => {
  try {
    const response = await axios.post(`${API_URL}/login`, {
      username,
      password,
    });
    return response.data;
  } catch (error) {
    console.error("Failed to login:", error.response.data);
    throw error;
  }
};

export const registerUser = async (username, password, email) => {
  try {
    const response = await axios.post(`${API_URL}/register`, {
      username,
      password,
      email,
    });
    return response.data;
  } catch (error) {
    console.error("Failed to register:", error.response.data);
    throw error;
  }
};

export const fetchUserPortfolio = async (username) => {
  try {
    const response = await axios.get(`${API_URL}/portfolio/${username}`);
    return response.data;
  } catch (error) {
    console.error("Failed to fetch portfolio:", error.response.data);
    throw error;
  }
};
