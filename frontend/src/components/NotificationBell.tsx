"use client";

import { Bell, CheckCheck } from "lucide-react";
import { useEffect, useState } from "react";
import { api, API_URL } from "@/lib/api";

type Notification = { id: number; category: string; severity: string; title: string; body: string; is_read: number; created_at: string };

export function NotificationBell() {
  const [items, setItems] = useState<Notification[]>([]);
  const [open, setOpen] = useState(false);
  const load = () => api<Notification[]>("/notifications").then(setItems).catch(() => undefined);

  useEffect(() => {
    void load();
    const timer = window.setInterval(load, 15000);
    const wsUrl = API_URL.replace(/^http/, "ws") + "/ws/events";
    const socket = new WebSocket(wsUrl);
    socket.onmessage = () => void load();
    const heartbeat = window.setInterval(() => socket.readyState === WebSocket.OPEN && socket.send("ping"), 25000);
    return () => { window.clearInterval(timer); window.clearInterval(heartbeat); socket.close(); };
  }, []);

  const unread = items.filter((item) => !item.is_read).length;
  const markAllRead = async () => {
    await Promise.all(items.filter((item) => !item.is_read).map((item) => api(`/notifications/${item.id}/read`, { method: "POST" })));
    await load();
  };
  return <div className="relative">
    <button onClick={() => setOpen(!open)} aria-expanded={open} aria-label="Open notifications" className="relative grid size-10 place-items-center rounded-full border border-stroke text-muted transition hover:text-white">
      <Bell size={17} />
      {unread > 0 && <span className="absolute -right-1 -top-1 grid min-w-5 place-items-center rounded-full bg-amber-200 px-1 py-0.5 text-[10px] font-semibold text-black">{unread > 9 ? "9+" : unread}</span>}
    </button>
    {open && <div className="absolute right-0 top-12 z-[70] w-[min(23rem,calc(100vw-2.5rem))] overflow-hidden rounded-3xl border border-stroke bg-surface shadow-2xl">
      <div className="flex items-center justify-between border-b border-stroke px-5 py-4"><div><p className="text-sm">Notifications</p><p className="mt-0.5 text-xs text-muted">Local workspace activity</p></div>{unread > 0 && <button onClick={markAllRead} className="flex items-center gap-1.5 text-xs text-[#c7dbef]"><CheckCheck size={14} /> Mark read</button>}</div>
      <div className="thin-scrollbar max-h-96 overflow-y-auto">
        {items.length ? items.map((item) => <div key={item.id} className={`border-b border-stroke px-5 py-4 last:border-0 ${item.is_read ? "opacity-60" : "bg-[#89aacc]/5"}`}><div className="flex items-center gap-2"><span className={`size-2 rounded-full ${item.severity === "action" ? "bg-amber-200" : item.severity === "error" ? "bg-red-300" : "bg-[#89aacc]"}`} /><p className="text-sm">{item.title}</p></div><p className="mt-2 text-xs leading-5 text-muted">{item.body}</p></div>) : <p className="px-5 py-10 text-center text-sm text-muted">Nothing needs your attention.</p>}
      </div>
    </div>}
  </div>;
}
