import { ArrowUpRight } from "lucide-react";
import Link from "next/link";

export function PillButton({ href, children, secondary = false }: { href: string; children: React.ReactNode; secondary?: boolean }) {
  return (
    <Link href={href} className={`gradient-border inline-flex items-center gap-2 rounded-full px-6 py-3 text-sm transition hover:scale-[1.03] ${secondary ? "border border-stroke bg-bg text-white" : "bg-white text-black"}`}>
      {children}<ArrowUpRight size={15} />
    </Link>
  );
}

export function Score({ value }: { value: number }) {
  const color = value >= 85 ? "#8ed7b5" : value >= 70 ? "#89aacc" : value >= 50 ? "#e1bd79" : "#d98484";
  return (
    <div className="relative grid size-16 place-items-center rounded-full" style={{ background: `conic-gradient(${color} ${value * 3.6}deg, #242424 0deg)` }}>
      <div className="grid size-[54px] place-items-center rounded-full bg-surface font-display text-xl italic">{value}%</div>
    </div>
  );
}

export function EmptyState({ title, text }: { title: string; text: string }) {
  return <div className="rounded-3xl border border-dashed border-stroke px-6 py-16 text-center"><p className="font-display text-3xl italic">{title}</p><p className="mx-auto mt-3 max-w-md text-sm leading-6 text-muted">{text}</p></div>;
}
