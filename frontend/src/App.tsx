import { useState } from "react";
import { ChatPage } from "./pages/ChatPage";
import { LoginPage } from "./pages/LoginPage";

export function App() {
  const [token, setToken] = useState<string | null>(null);
  const [userId, setUserId] = useState("");

  if (!token) {
    return <LoginPage onAuthenticated={(uid, jwt) => { setUserId(uid); setToken(jwt); }} />;
  }
  return <ChatPage token={token} userId={userId} />;
}
