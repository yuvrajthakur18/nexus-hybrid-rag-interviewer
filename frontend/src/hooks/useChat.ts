import { useState } from "react";
import { chatQueryStream } from "../services/api";

export type SourceCitation = { source: string; chunk_id: string; score: number };
export type Message = { 
  role: "user" | "assistant"; 
  content: string; 
  citations?: SourceCitation[];
  thoughts?: string[];
  isComplete?: boolean;
};

export function useChat(token: string, userId: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState<number | undefined>(undefined);
  const [loading, setLoading] = useState(false);

  const send = async (query: string) => {
    setLoading(true);
    setMessages((m) => [...m, { role: "user", content: query }]);
    
    // Add empty assistant message to fill in
    setMessages((m) => [...m, { role: "assistant", content: "" }]);

    try {
      const response = await chatQueryStream(token, userId, query, sessionId);
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      if (!reader) throw new Error("No reader");

      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        // Keep the last partial line in the buffer
        buffer = lines.pop() || "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed || !trimmed.startsWith("data: ")) continue;
          
          try {
            const data = JSON.parse(trimmed.slice(6));
            
            setMessages((prevMessages) => {
              const lastMessage = prevMessages[prevMessages.length - 1];
              if (!lastMessage || lastMessage.role !== "assistant") return prevMessages;

              const updatedMessages = [...prevMessages.slice(0, -1)];
              const updatedLastMessage = { ...lastMessage };

              if (data.type === "metadata") {
                updatedLastMessage.citations = data.citations || [];
              } else if (data.type === "content") {
                updatedLastMessage.content = (updatedLastMessage.content || "") + data.answer;
              } else if (data.type === "thought") {
                updatedLastMessage.thoughts = [...(updatedLastMessage.thoughts || []), data.message];
              } else if (data.type === "final") {
                updatedLastMessage.isComplete = true;
              }
              
              if (data.session_id) setSessionId(data.session_id);
              
              updatedMessages.push(updatedLastMessage);
              return updatedMessages;
            });
          } catch (e) {
            console.error("SSE parse error", e, trimmed);
          }
        }
      }
    } catch (err) {
      console.error("Stream error", err);
      setMessages((m) => [...m, { role: "assistant", content: "Error: Could not reach the Nexus core." }]);
    } finally {
      setLoading(false);
    }
  };

  return { messages, send, loading };
}
