import { ChatWindow } from "../components/ChatWindow";

type Props = { token: string; userId: string };

export function ChatPage({ token, userId }: Props) {
  return (
    <main className="min-h-screen p-6 md:p-12 relative z-10 flex flex-col animate-fade-in">
      <div className="max-w-4xl w-full mx-auto flex-1 flex flex-col">
        <header className="mb-8 flex flex-col sm:flex-row sm:items-end justify-between border-b border-white/10 pb-4">
          <div>
            <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
              Nexus Architect
            </h2>
            <p className="mt-1 text-sm text-slate-400">
              Identity Confirmed: <span className="text-indigo-300 font-semibold tracking-wide ml-1">{userId}</span>
            </p>
          </div>
          <div className="mt-4 sm:mt-0">
             <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
               <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
               Secure Session Active
             </div>
          </div>
        </header>
        
        <div className="flex-1 flex flex-col h-full glass-panel rounded-3xl overflow-hidden shadow-2xl shadow-indigo-900/20">
          <ChatWindow token={token} userId={userId} />
        </div>
      </div>
      
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        .animate-fade-in {
          animation: fadeIn 0.8s ease-in-out forwards;
        }
      `}</style>
    </main>
  );
}
