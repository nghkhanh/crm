import { redirect } from "next/navigation";

export default function ReconciliationsRedirectPage() {
  redirect("/transactions");
}
