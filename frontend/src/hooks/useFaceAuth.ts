import { useState } from "react";
import { enrollFace, verifyFace } from "../services/api";

export function useFaceAuth() {
  const [loading, setLoading] = useState(false);

  const enroll = async (userId: string, imageSequence: string[]) => {
    setLoading(true);
    try {
      await enrollFace(userId, imageSequence);
    } finally {
      setLoading(false);
    }
  };

  const verify = async (userId: string, imageSequence: string[], challenge: string) => {
    setLoading(true);
    try {
      return await verifyFace(userId, imageSequence, challenge);
    } finally {
      setLoading(false);
    }
  };

  return { loading, enroll, verify };
}
