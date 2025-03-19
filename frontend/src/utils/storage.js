export const getToke = () => {
  if (typeof window !== "undefined") {
    return localStorage.getItem("access_token");
  }
  return null;
};

export const getRefreshToken = () => {
  if (typeof window !== "undefined") {
    return localStorage.getItem("refresh_token");
  }
  return null;
};

export const setToken = (accessToken, refreshToken) => {
  if (typeof window !== "undefined") {
    localStorage.setItem("access_token", accessToken);
    localStorage.setItem("refresh_token", refreshToken);
  }
};

export const removeToken = () => {
  if (typeof window !== "undefined") {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  }
};

export const refreshToken = async () => {
  try {
    const refreshToken = getRefreshToken();
    if (!refreshToken) return false;

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/auth/jwt/refresh/`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ refresh: refreshToken }),
      }
    );

    if (!response.ok) return false;

    const data = await response.json();
    setToken(data.access, refreshToken);
    return true;
  } catch (error) {
    console.error("Token refresh failed:", error);
    return false;
  }
};
