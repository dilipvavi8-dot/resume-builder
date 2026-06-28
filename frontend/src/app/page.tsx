"use client";

import { motion } from "framer-motion";
import gsap from "gsap";
import { ArrowRight, Bot, BriefcaseBusiness, FileSearch, LockKeyhole, WandSparkles } from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { BrandMark } from "@/components/BrandMark";
import { LoadingScreen } from "@/components/LoadingScreen";
import { PillButton } from "@/components/Ui";
import { VideoBackground } from "@/components/VideoBackground";

const roles = ["DevOps", "SRE", "Platform", "AI Cloud"];
const features = [
  { title: "Daily job intelligence", text: "A focused feed for cloud, platform, reliability, automation, and AI infrastructure roles.", icon: BriefcaseBusiness, span: "md:col-span-7" },
  { title: "JD analysis", text: "Extract skills, experience, cloud platforms, ATS language, and the gaps that matter.", icon: FileSearch, span: "md:col-span-5" },
  { title: "Private by design", text: "SQLite and local file storage. No accounts, no cloud resume vault, no auto-applying.", icon: LockKeyhole, span: "md:col-span-5" },
  { title: "Tailored resume studio", text: "Generate a new DOCX version for the role while preserving your real experience.", icon: WandSparkles, span: "md:col-span-7" },
];

export default function Home() {
  const [loading, setLoading] = useState(true);
  const [role, setRole] = useState(0);
  const root = useRef<HTMLDivElement>(null);
  const onComplete = useCallback(() => setLoading(false), []);

  useEffect(() => {
    const interval = window.setInterval(() => setRole((value) => (value + 1) % roles.length), 2000);
    return () => clearInterval(interval);
  }, []);

  useLayoutEffect(() => {
    if (loading || !root.current) return;
    const context = gsap.context(() => {
      gsap.timeline({ defaults: { ease: "power3.out" } })
        .from(".name-reveal", { opacity: 0, y: 50, duration: 1.2, delay: 0.1 })
        .from(".blur-in", { opacity: 0, filter: "blur(10px)", y: 20, duration: 1, stagger: 0.1 }, "-=.7");
    }, root);
    const visibilityFallback = window.setTimeout(() => {
      gsap.set(".name-reveal, .blur-in", { opacity: 1, y: 0, filter: "blur(0px)" });
    }, 1800);
    return () => {
      clearTimeout(visibilityFallback);
      context.revert();
    };
  }, [loading]);

  return (
    <div ref={root} className="w-full max-w-[100vw] overflow-x-hidden">
      {loading && <LoadingScreen onComplete={onComplete} />}
      <nav className="fixed inset-x-0 top-0 z-50 flex justify-center px-4 pt-4 md:pt-6">
        <div className="glass flex items-center rounded-full p-2 shadow-xl shadow-black/20">
          <Link href="/" aria-label="Rolecraft home" className="flex items-center gap-2"><BrandMark /><span className="hidden font-display text-xl italic text-white sm:inline">Rolecraft</span></Link>
          <span className="mx-2 hidden h-5 w-px bg-stroke sm:block" />
          <a href="#workflow" className="hidden rounded-full px-3 py-2 text-xs text-muted hover:bg-stroke/50 hover:text-white sm:block sm:px-4 sm:text-sm">Workflow</a>
          <a href="#features" className="hidden rounded-full px-3 py-2 text-xs text-muted hover:bg-stroke/50 hover:text-white sm:block sm:px-4 sm:text-sm">Product</a>
          <span className="mx-2 hidden h-5 w-px bg-stroke sm:block" />
          <Link href="/dashboard" className="rounded-full bg-white px-4 py-2 text-xs text-black sm:text-sm">Open app ↗</Link>
        </div>
      </nav>

      <section className="relative flex min-h-screen w-full max-w-[100vw] items-center justify-center overflow-hidden px-6 text-center">
        <VideoBackground />
        <div className="absolute inset-0 bg-black/50" />
        <div className="noise absolute inset-0 opacity-20 mix-blend-soft-light" />
        <div className="absolute inset-x-0 bottom-0 h-56 bg-gradient-to-t from-bg to-transparent" />
        <div className="relative z-10 mx-auto w-full min-w-0 max-w-6xl pt-20">
          <p className="blur-in mx-auto mb-8 max-w-[290px] px-3 text-[9px] uppercase leading-5 tracking-[0.18em] text-white/60 sm:max-w-none sm:text-[10px] sm:tracking-[0.4em]">Your next role / thoughtfully engineered</p>
          <h1 className="name-reveal px-2 font-display text-[2.65rem] italic leading-[0.9] tracking-tight sm:hidden"><span className="block">Make your</span><span className="block">experience</span><span className="block">impossible to miss.</span></h1>
          <h1 className="name-reveal hidden max-w-full px-2 font-display italic leading-[0.9] tracking-tight sm:block sm:text-6xl md:text-8xl lg:text-[9rem]">Make your experience<br />impossible to miss.</h1>
          <p className="blur-in mx-auto mt-7 max-w-[310px] text-sm text-white/65 md:max-w-none md:text-base">A <span key={role} className="animate-role-fade-in font-display text-xl italic text-white">{roles[role]}</span> career copilot, running locally.</p>
          <p className="blur-in mx-auto mt-5 max-w-[310px] text-sm leading-7 text-white/60 sm:max-w-xl md:text-base">Discover relevant roles, understand exactly where you match, and shape a stronger resume without losing your voice or inventing experience.</p>
          <div className="blur-in mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row sm:flex-wrap sm:gap-4"><PillButton href="/dashboard">Enter workspace</PillButton><PillButton href="/manual-jd" secondary>Analyze a JD</PillButton></div>
        </div>
        <a href="#workflow" className="absolute bottom-8 z-10 flex flex-col items-center gap-3 text-[9px] uppercase tracking-[0.3em] text-muted">
          Scroll<div className="relative h-10 w-px overflow-hidden bg-stroke"><span className="animate-scroll-down absolute inset-x-0 h-5 accent-gradient" /></div>
        </a>
      </section>

      <section id="workflow" className="px-6 py-24 md:px-10 md:py-32">
        <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: "-100px" }} className="mx-auto max-w-6xl">
          <div className="flex items-end justify-between gap-8">
            <div><p className="mb-5 flex items-center gap-3 text-[10px] uppercase tracking-[0.35em] text-muted"><span className="h-px w-8 bg-stroke" /> The workflow</p><h2 className="font-display text-5xl leading-none md:text-7xl">From job noise to<br /><em className="accent-text">clear next move.</em></h2></div>
            <p className="hidden max-w-sm text-sm leading-7 text-muted md:block">One calm system for discovery, analysis, resume versions, and application follow-through.</p>
          </div>
          <div id="features" className="mt-16 grid grid-cols-1 gap-5 md:grid-cols-12">
            {features.map(({ title, text, icon: Icon, span }, index) => (
              <motion.article key={title} initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.08 }} viewport={{ once: true }} className={`group relative min-h-72 overflow-hidden rounded-[2rem] border border-stroke bg-surface p-8 md:p-10 ${span}`}>
                <div className="absolute right-0 top-0 size-64 rounded-full bg-blue-400/5 blur-3xl transition group-hover:bg-blue-400/10" />
                <Icon className="text-[#89aacc]" size={28} />
                <div className="absolute inset-x-8 bottom-8"><p className="font-display text-3xl italic md:text-4xl">{title}</p><p className="mt-3 max-w-lg text-sm leading-7 text-muted">{text}</p></div>
                <span className="absolute right-7 top-7 grid size-9 place-items-center rounded-full border border-stroke text-muted transition group-hover:border-white/30 group-hover:text-white"><ArrowRight size={15} /></span>
              </motion.article>
            ))}
          </div>
        </motion.div>
      </section>

      <section className="border-y border-stroke px-6 py-20">
        <div className="mx-auto grid max-w-6xl gap-10 text-center md:grid-cols-3">
          {[["01", "Master resume"], ["100%", "Local storage"], ["08:00", "Daily fetch ready"]].map(([value, label]) => <div key={label}><p className="font-display text-6xl italic">{value}</p><p className="mt-2 text-[10px] uppercase tracking-[0.3em] text-muted">{label}</p></div>)}
        </div>
      </section>

      <footer className="relative overflow-hidden px-6 pb-10 pt-28 text-center md:pt-36">
        <VideoBackground flip />
        <div className="absolute inset-0 bg-black/75" />
        <div className="absolute inset-x-0 top-0 h-56 bg-gradient-to-b from-bg to-transparent" />
        <div className="relative z-10 mx-auto max-w-4xl"><Bot className="mx-auto mb-8 text-[#89aacc]" /><p className="text-[10px] uppercase tracking-[0.4em] text-white/50">Ready when you are</p><h2 className="mt-5 font-display text-6xl italic md:text-8xl">Build the next version<br />of your career.</h2><div className="mt-10"><PillButton href="/dashboard">Launch Rolecraft</PillButton></div></div>
        <div className="relative z-10 mx-auto mt-28 flex max-w-6xl flex-col justify-between gap-4 border-t border-white/10 pt-6 text-xs text-white/45 sm:flex-row"><p>Rolecraft</p><p><span className="mr-2 inline-block size-2 rounded-full bg-emerald-400 shadow-[0_0_10px_#34d399]" />Local workspace available</p></div>
      </footer>
    </div>
  );
}
