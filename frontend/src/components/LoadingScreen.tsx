"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useState } from "react";

export function LoadingScreen({ onComplete }: { onComplete: () => void }) {
  const [count, setCount] = useState(0);
  const [word, setWord] = useState(0);
  const words = ["Discover", "Align", "Advance"];

  useEffect(() => {
    const started = performance.now();
    let frame = 0;
    let completed = false;
    const finish = () => {
      if (completed) return;
      completed = true;
      setCount(100);
      window.setTimeout(onComplete, 320);
    };
    const tick = (now: number) => {
      const next = Math.min(100, Math.floor(((now - started) / 2200) * 100));
      setCount(next);
      if (next < 100) frame = requestAnimationFrame(tick);
      else finish();
    };
    frame = requestAnimationFrame(tick);
    const interval = window.setInterval(() => setWord((value) => (value + 1) % words.length), 730);
    const fallback = window.setTimeout(finish, 2800);
    return () => {
      cancelAnimationFrame(frame);
      clearInterval(interval);
      clearTimeout(fallback);
    };
  }, [onComplete, words.length]);

  return (
    <motion.div exit={{ opacity: 0 }} className="fixed inset-0 z-[9999] bg-bg">
      <motion.p initial={{ y: -20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="absolute left-6 top-6 text-[10px] uppercase tracking-[0.35em] text-muted md:left-10 md:top-10">
        Rolecraft / Local AI
      </motion.p>
      <div className="absolute inset-0 grid place-items-center">
        <AnimatePresence mode="wait">
          <motion.p key={words[word]} initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: -20, opacity: 0 }} className="font-display text-5xl italic text-white/80 md:text-7xl">
            {words[word]}
          </motion.p>
        </AnimatePresence>
      </div>
      <p className="absolute bottom-10 right-6 font-display text-7xl tabular-nums md:bottom-12 md:right-10 md:text-9xl">
        {String(count).padStart(3, "0")}
      </p>
      <div className="absolute inset-x-0 bottom-0 h-[3px] bg-stroke/50">
        <div className="accent-gradient h-full origin-left" style={{ transform: `scaleX(${count / 100})`, boxShadow: "0 0 8px rgba(137,170,204,.35)" }} />
      </div>
    </motion.div>
  );
}
