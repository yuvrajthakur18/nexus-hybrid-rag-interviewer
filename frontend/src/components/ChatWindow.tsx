import { useState, useRef, useEffect } from "react";
import { useChat } from "../hooks/useChat";
import { SourceCitations } from "./SourceCitations";

type Props = { token: string; userId: string };

export function ChatWindow({ token, userId }: Props) {
  const [query, setQuery] = useState("");
  const { messages, send, loading } = useChat(token, userId);
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  return (
    <section className="flex flex-col h-full w-full max-h-[80vh]">
      {/* Chat History Area */}
      <div className="flex-1 overflow-y-auto p-6 scroll-smooth custom-scrollbar">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center opacity-70">
            <div className="w-16 h-16 rounded-2xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-slate-200">Session Initialized</h3>
            <p className="mt-2 text-sm text-slate-400 max-w-sm">
              Your biometric identity is verified. You can now securely interact with the Nexus: Character Design Architect Core.
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {messages.map((m, i) => {
              const isUser = m.role === "user";
              return (
                <div key={i} className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'}`}>
                  <div className={`flex flex-col max-w-[85%] sm:max-w-[75%] ${isUser ? 'items-end' : 'items-start'}`}>
                    <div className="flex items-center gap-2 mb-1.5 px-1">
                      <span className="text-[10px] uppercase font-bold tracking-wider text-slate-500">
                        {isUser ? userId : 'Nexus Architect'}
                      </span>
                    </div>
                    
                    <div className={`p-4 rounded-2xl shadow-lg relative ${isUser ? 'bg-indigo-600/90 text-white rounded-tr-sm border border-indigo-500/50' : 'bg-slate-800/80 text-slate-100 rounded-tl-sm border border-white/10 backdrop-blur-md'}`}>
                      {!isUser && m.thoughts && m.thoughts.length > 0 && (
                        <details open={!m.isComplete} className="group mb-3 border-b border-white/5 pb-2">
                          <summary className="flex items-center gap-2 cursor-pointer list-none text-xs font-semibold text-slate-400 hover:text-indigo-400 transition-colors">
                            <svg className="w-3.5 h-3.5 group-open:rotate-90 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5l7 7-7 7" />
                            </svg>
                            <div className="flex items-center gap-2">
                              <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse" />
                              REASONING LOG
                            </div>
                          </summary>
                          <ul className="mt-2 space-y-1.5 pl-5 border-l-2 border-slate-700/50">
                            {m.thoughts.map((t, ti) => (
                              <li key={ti} className="text-[11px] text-slate-400 font-mono tracking-tight leading-relaxed">
                                <span className="text-indigo-500/70 mr-2">›</span>
                                {t}
                              </li>
                            ))}
                          </ul>
                        </details>
                      )}

                      <p className="text-sm leading-relaxed whitespace-pre-wrap font-inter">
                        {m.content}
                      </p>
                      
                      {!isUser && m.citations && m.citations.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-white/10">
                          <SourceCitations citations={m.citations} />
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
            
            {loading && (
              <div className="flex justify-start">
                <div className="bg-slate-800/80 rounded-2xl rounded-tl-sm border border-white/10 backdrop-blur-md p-4 flex gap-1.5 items-center">
                  <span className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{animationDelay: "0ms"}}/>
                  <span className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{animationDelay: "150ms"}}/>
                  <span className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{animationDelay: "300ms"}}/>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-4 sm:p-6 bg-slate-900/60 backdrop-blur-xl border-t border-white/10">
        <div className="relative flex items-end gap-3 max-w-4xl mx-auto">
          <textarea
            ref={textareaRef}
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              // Auto-expand logic
              e.target.style.height = 'inherit';
              const nextHeight = e.target.scrollHeight;
              e.target.style.height = `${Math.min(nextHeight, 160)}px`;
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (!loading && query.trim()) {
                  send(query);
                  setQuery("");
                  if (textareaRef.current) textareaRef.current.style.height = 'inherit';
                }
              }
            }}
            placeholder="Type your query... (Shift+Enter for new line)"
            className="glass-input flex-1 min-h-[56px] max-h-40 rounded-2xl px-5 py-4 text-sm resize-none custom-scrollbar transition-[height] duration-100"
            rows={1}
          />
          <button
            disabled={loading || !query.trim()}
            onClick={() => {
              send(query);
              setQuery("");
            }}
            className="premium-btn shrink-0 w-14 h-14 rounded-2xl bg-indigo-600 hover:bg-indigo-500 shadow-[0_0_15px_rgba(99,102,241,0.4)] flex items-center justify-center text-white border border-indigo-400/50"
            title="Send Message"
          >
            {loading ? (
               <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"/>
            ) : (
              <svg className="w-5 h-5 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            )}
          </button>
        </div>
      </div>
      
      <style>{`
        .custom-scrollbar::-webkit-scrollbar { width: 6px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }
      `}</style>
    </section>
  );
}
