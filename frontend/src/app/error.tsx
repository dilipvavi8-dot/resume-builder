"use client";
export default function ErrorPage({ reset }: { reset: () => void }) { return <div className="grid min-h-screen place-items-center bg-bg px-6 text-center"><div><p className="font-display text-4xl italic">Something interrupted the flow.</p><button onClick={reset} className="mt-6 rounded-full bg-white px-5 py-3 text-sm text-black">Try again</button></div></div>; }
