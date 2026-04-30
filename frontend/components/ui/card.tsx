import { ReactNode } from "react";
import clsx from "clsx";

export function Card({
  children,
  className
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={clsx("rounded-[24px] border border-[#e3eaf4] bg-white p-5 shadow-[0_10px_30px_rgba(15,23,42,0.05)]", className)}>
      {children}
    </section>
  );
}
